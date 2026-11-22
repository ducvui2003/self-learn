"""Common REST Dispatcher View (like Spring DispatcherServlet + @RestControllerAdvice).

Why companies split handlers into GET.py, POST.py, PUT.py, PATCH.py, DELETE.py:
- Zope's <browser:page> always enters `__call__()` regardless of HTTP method.
- This single base class handles cross-cutting concerns ONCE:
    1. Path traversal (`IPublishTraverse` -> `self.subpath`)
    2. CORS headers + `OPTIONS` preflight (`204 No Content`)
    3. HTTP verb routing (`GET` -> GET.py, `POST` -> POST.py, ...)
    4. Global JSON error handling (catches ApiError & unexpected Exception -> never leaks HTML)
    5. Automatic `transaction.abort()` on unexpected 500 errors
"""

import json
import logging

from Products.Five.browser import BrowserView
import transaction
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from ..exceptions import ApiError
from ..models import now_jst_iso

logger = logging.getLogger("employee_api.rest")


class BaseMethodHandler:
    """Base class for per-verb handler classes (GET.py, POST.py, PUT.py, etc.)."""

    def __init__(self, context, request, subpath):
        self.context = context
        self.request = request
        self.subpath = subpath

    def read_json_body(self):
        raw = self.request.get("BODY", b"")
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        if not raw or not raw.strip():
            return {}
        try:
            data = json.loads(raw)
        except ValueError:
            raise ApiError("E_INVALID_JSON", "Request body must be valid JSON.", status=400)
        if not isinstance(data, dict):
            raise ApiError("E_INVALID_JSON", "Request body must be a JSON object.", status=400)
        return data

    def query_param(self, name, default=""):
        return str(self.request.form.get(name, default)).strip()

    def query_int(self, name, default, min_val=1, max_val=100):
        raw = self.query_param(name, "")
        if not raw:
            return default
        try:
            val = int(raw)
        except ValueError:
            raise ApiError("E_VALIDATION", f"Query param '{name}' must be an integer.", status=400)
        return max(min_val, min(val, max_val))

    def handle(self):
        """Override in subclass; return `(data_dict, http_status)`."""
        raise NotImplementedError


@implementer(IPublishTraverse)
class RestDispatcherView(BrowserView):
    """Dispatches HTTP verbs to `handlers = {'GET': ..., 'POST': ...}` subclasses."""

    # Subclasses override this dict to plug in GET.py, POST.py, PUT.py, PATCH.py, DELETE.py
    handlers = {}
    allowed_origin = "*"

    def __init__(self, context, request):
        super().__init__(context, request)
        self.subpath = []

    def publishTraverse(self, request, name):
        self.subpath.append(name)
        return self

    def __call__(self):
        self._apply_cors_headers()
        method = self.request.method.upper()

        # 1. Handle CORS preflight automatically (like Spring @CrossOrigin)
        if method == "OPTIONS":
            self.request.response.setStatus(204)
            return ""

        # 2. Look up handler class for this HTTP verb (GET.py, POST.py, etc.)
        handler_cls = self.handlers.get(method)
        if handler_cls is None:
            allowed = ", ".join(sorted(list(self.handlers.keys()) + ["OPTIONS"]))
            self.request.response.setHeader("Allow", allowed)
            return self._write_error(
                code="E_METHOD_NOT_ALLOWED",
                message=f"HTTP method '{method}' is not allowed on this endpoint.",
                status=405,
            )

        # 3. Execute handler inside global error boundary (like @RestControllerAdvice)
        try:
            handler = handler_cls(self.context, self.request, self.subpath)
            result = handler.handle()
            if isinstance(result, tuple):
                data, status = result
            else:
                data, status = result, 200
            return self._write_ok(data, status=status)

        except ApiError as err:
            return self._write_error(
                code=err.code,
                message=err.message,
                status=err.status,
                details=err.details,
            )

        except Exception:
            # Never leak raw Python/Zope HTML tracebacks to REST clients!
            transaction.abort()
            logger.exception("Unhandled error during %s /%s", method, "/".join(self.subpath))
            return self._write_error(
                code="E_INTERNAL_ERROR",
                message="An unexpected internal server error occurred.",
                status=500,
            )

    def _apply_cors_headers(self):
        response = self.request.response
        allowed = ", ".join(sorted(list(self.handlers.keys()) + ["OPTIONS"]))
        response.setHeader("Access-Control-Allow-Origin", self.allowed_origin)
        response.setHeader("Access-Control-Allow-Methods", allowed)
        response.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def _write_ok(self, data, status=200):
        payload = {
            "status": "ok",
            "data": data,
            "timestamp": now_jst_iso(),
        }
        return self._write_json(payload, status)

    def _write_error(self, code, message, status=400, details=None):
        error_obj = {"code": code, "message": message}
        if details is not None:
            error_obj["details"] = details
        payload = {
            "status": "error",
            "error": error_obj,
            "timestamp": now_jst_iso(),
        }
        return self._write_json(payload, status)

    def _write_json(self, payload, status):
        response = self.request.response
        response.setStatus(status)
        response.setHeader("Content-Type", "application/json; charset=utf-8")
        return json.dumps(payload, ensure_ascii=False, indent=2)
