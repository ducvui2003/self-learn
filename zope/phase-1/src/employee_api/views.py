"""Phase 1 REST API views (Spring @RestController equivalent).

Each BrowserView receives two objects automatically:
- self.context : the Zope object that was traversed to (here, the Zope root "/")
- self.request : the HTTP request/response object (like HttpServletRequest + HttpServletResponse)
"""

from datetime import datetime, timezone, timedelta
import json

from Products.Five.browser import BrowserView
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from .data import EMPLOYEES

JST = timezone(timedelta(hours=9))


class BaseJsonView(BrowserView):
    """Helper base class for consistent Japan-enterprise JSON responses.

    Spring equivalent: a base ResponseEntity helper or @RestControllerAdvice wrapper.
    """

    def json_ok(self, data, status=200):
        """Return a standard success JSON envelope."""
        payload = {
            "status": "ok",
            "data": data,
            "timestamp": datetime.now(JST).isoformat(),
        }
        return self._write_json(payload, status)

    def json_error(self, code, message, status=400):
        """Return a standard error JSON envelope with a business error code."""
        payload = {
            "status": "error",
            "error": {
                "code": code,
                "message": message,
            },
            "timestamp": datetime.now(JST).isoformat(),
        }
        return self._write_json(payload, status)

    def _write_json(self, payload, status):
        response = self.request.response
        response.setStatus(status)
        # IMPORTANT: Always set Content-Type with charset=utf-8.
        # Otherwise Zope may guess text/html or break Japanese characters.
        response.setHeader("Content-Type", "application/json; charset=utf-8")
        # ensure_ascii=False keeps Japanese text readable ("営業部" instead of "\u55b6...")
        return json.dumps(payload, ensure_ascii=False, indent=2)


class HealthApiView(BaseJsonView):
    """GET /api-health — simple health check endpoint.

    Spring equivalent: Spring Boot Actuator /actuator/health or @GetMapping("/api-health").
    """

    def __call__(self):
        return self.json_ok(
            {
                "service": "zope-phase1-employee-api",
                "zopeContextId": self.context.getId(),
                "message": "Zope 5 WSGI server is running",
            }
        )


@implementer(IPublishTraverse)
class EmployeesApiView(BaseJsonView):
    """Employee REST API demonstrating Zope Traversal + Query Params.

    Spring equivalent:
      @GetMapping("/api-employees")                -> list (optional ?dept=...)
      @GetMapping("/api-employees/{empCode}")      -> get single employee

    In Zope, URL path segments are resolved by traversal, not regex routes.
    Implementing IPublishTraverse lets this view capture the next URL segment
    ("/api-employees/EMP-0001" -> name = "EMP-0001").
    """

    def __init__(self, context, request):
        super().__init__(context, request)
        self.subpath = []

    def publishTraverse(self, request, name):
        """Called by Zope's publisher for each extra segment after /api-employees."""
        self.subpath.append(name)
        return self

    def __call__(self):
        # Case 1: GET /api-employees (no extra path segment)
        if not self.subpath:
            return self._list_employees()

        # Case 2: GET /api-employees/{empCode}
        if len(self.subpath) == 1:
            return self._get_employee(self.subpath[0])

        # Case 3: Too many path segments (e.g. /api-employees/EMP-0001/extra)
        return self.json_error(
            code="E_INVALID_PATH",
            message="Unsupported path: /" + "/".join(self.subpath),
            status=404,
        )

    def _list_employees(self):
        # self.request.form holds query parameters (like @RequestParam in Spring)
        dept_filter = self.request.form.get("dept", "").strip().lower()

        items = EMPLOYEES
        if dept_filter:
            items = [
                emp
                for emp in EMPLOYEES
                if dept_filter in emp["departmentEn"].lower()
                or dept_filter in emp["departmentJa"]
            ]

        return self.json_ok(
            {
                "items": items,
                "totalCount": len(items),
            }
        )

    def _get_employee(self, emp_code):
        for emp in EMPLOYEES:
            if emp["empCode"].upper() == emp_code.upper():
                return self.json_ok(emp)

        return self.json_error(
            code="E_NOT_FOUND",
            message=f"Employee '{emp_code}' was not found.",
            status=404,
        )
