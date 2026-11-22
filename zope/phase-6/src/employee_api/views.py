"""Phase 6 Production-Ready REST Views: Indexed Search + Structured Request Logging.

Japan-enterprise observability tip:
- Every request gets a unique `X-Request-Id` header and structured log line
  (requestId, method, path, status, durationMs) for fast incident checks (障害調査).
"""

import json
import logging
import time
import uuid

from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from .catalog import Employee, get_or_create_indexed_store, now_jst_iso

logger = logging.getLogger("employee_api.access")


class ObservableJsonView(BrowserView):
    """Base view adding X-Request-Id + execution timing logs (like Spring OncePerRequestFilter)."""

    def __call__(self):
        start = time.perf_counter()
        request_id = self.request.getHeader("X-Request-Id") or str(uuid.uuid4())[:8]
        self.request.response.setHeader("X-Request-Id", request_id)
        status = 200
        try:
            body_str, status = self.dispatch(request_id)
            return body_str
        finally:
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
            logger.info(
                "requestId=%s method=%s path=%s status=%s durationMs=%s",
                request_id,
                self.request.method,
                self.request.get("PATH_INFO", ""),
                status,
                elapsed_ms,
            )

    def dispatch(self, request_id):
        raise NotImplementedError

    def read_json_body(self):
        raw = self.request.get("BODY", b"")
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return json.loads(raw) if raw and raw.strip() else {}

    def json_ok(self, data, request_id, status=200):
        payload = {
            "status": "ok",
            "requestId": request_id,
            "data": data,
            "timestamp": now_jst_iso(),
        }
        return self._write(payload, status), status

    def json_error(self, code, message, request_id, status=400):
        payload = {
            "status": "error",
            "requestId": request_id,
            "error": {"code": code, "message": message},
            "timestamp": now_jst_iso(),
        }
        return self._write(payload, status), status

    def _write(self, payload, status):
        response = self.request.response
        response.setStatus(status)
        response.setHeader("Content-Type", "application/json; charset=utf-8")
        return json.dumps(payload, ensure_ascii=False, indent=2)


class HealthApiView(ObservableJsonView):
    """GET /@@api-health — production readiness probe (for Nginx / Kubernetes)."""

    def dispatch(self, request_id):
        store = get_or_create_indexed_store(self.context)
        return self.json_ok(
            {
                "service": "zope-phase6-production-api",
                "status": "UP",
                "indexedDepartments": list(store.by_dept.keys()),
                "indexedSkillsCount": len(store.by_skill),
            },
            request_id=request_id,
        )


@implementer(IPublishTraverse)
class IndexedEmployeesApiView(ObservableJsonView):
    """GET /@@api-employees?dept=Engineering&skill=MySQL & POST /@@api-employees."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.subpath = []

    def publishTraverse(self, request, name):
        self.subpath.append(name)
        return self

    def dispatch(self, request_id):
        store = get_or_create_indexed_store(self.context)
        method = self.request.method.upper()

        if not self.subpath:
            if method == "GET":
                dept = self.request.form.get("dept", "")
                skill = self.request.form.get("skill", "")
                matches = store.search_indexed(dept=dept, skill=skill)
                return self.json_ok(
                    {
                        "items": [e.to_dict() for e in matches],
                        "totalCount": len(matches),
                        "indexedQuery": {"dept": dept or None, "skill": skill or None},
                    },
                    request_id=request_id,
                )

            if method == "POST":
                try:
                    body = self.read_json_body()
                except ValueError:
                    return self.json_error("E_INVALID_JSON", "Invalid JSON body.", request_id, 400)

                emp_code = str(body.get("empCode", "")).strip().upper()
                if not emp_code or not str(body.get("nameEn", "")).strip():
                    return self.json_error(
                        "E_VALIDATION", "empCode and nameEn are required.", request_id, 400
                    )
                if emp_code in store.employees:
                    return self.json_error(
                        "E_DUPLICATE", f"Employee '{emp_code}' already exists.", request_id, 409
                    )

                emp = Employee(
                    emp_code=emp_code,
                    name_en=body["nameEn"].strip(),
                    name_ja=body.get("nameJa", body["nameEn"]).strip(),
                    department_en=body.get("departmentEn", "Engineering").strip(),
                    department_ja=body.get("departmentJa", "開発部").strip(),
                    role=body.get("role", "Engineer").strip(),
                    skills=body.get("skills", []),
                )
                store.index_employee(emp)
                return self.json_ok(emp.to_dict(), request_id=request_id, status=201)

            return self.json_error("E_METHOD_NOT_ALLOWED", f"{method} not allowed", request_id, 405)

        if len(self.subpath) == 1 and method == "GET":
            emp_code = self.subpath[0].upper()
            emp = store.employees.get(emp_code)
            if emp is None or emp.deleted_flg:
                return self.json_error("E_NOT_FOUND", f"Employee '{emp_code}' not found.", request_id, 404)
            return self.json_ok(emp.to_dict(), request_id=request_id)

        return self.json_error("E_INVALID_PATH", "Unsupported path.", request_id, 404)
