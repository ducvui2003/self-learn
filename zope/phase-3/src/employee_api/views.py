"""Phase 3 Thin REST Views using ZCA Dependency Lookup (getUtility + Adapter).

Compare with Spring @RestController:
  - `getUtility(IEmployeeService)` ≈ `@Autowired EmployeeService`
  - `IEmployeeSerializer(emp)`     ≈ `employeeMapper.toDto(emp)` (ZCA Adapter)
"""

import json

from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from .interfaces import IAuditLogUtility, IEmployeeSerializer, IEmployeeService
from .models import now_jst_iso
from .services import ServiceError


class BaseJsonView(BrowserView):
    """Base helper for consistent Japan-enterprise JSON responses."""

    def read_json_body(self):
        raw = self.request.get("BODY", b"")
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        if not raw or not raw.strip():
            return {}
        return json.loads(raw)

    def json_ok(self, data, status=200):
        payload = {
            "status": "ok",
            "data": data,
            "timestamp": now_jst_iso(),
        }
        return self._write_json(payload, status)

    def json_error(self, code, message, status=400):
        payload = {
            "status": "error",
            "error": {"code": code, "message": message},
            "timestamp": now_jst_iso(),
        }
        return self._write_json(payload, status)

    def _write_json(self, payload, status):
        response = self.request.response
        response.setStatus(status)
        response.setHeader("Content-Type", "application/json; charset=utf-8")
        return json.dumps(payload, ensure_ascii=False, indent=2)


class HealthApiView(BaseJsonView):
    """GET /api-health — shows wired ZCA utilities."""

    def __call__(self):
        service = getUtility(IEmployeeService)
        audit = getUtility(IAuditLogUtility)
        return self.json_ok(
            {
                "service": "zope-phase3-zca-api",
                "employeeServiceClass": service.__class__.__name__,
                "auditUtilityClass": audit.__class__.__name__,
                "activeEmployees": len(service.list_employees(self.context)),
            }
        )


@implementer(IPublishTraverse)
class EmployeesApiView(BaseJsonView):
    """Thin REST Controller delegating to IEmployeeService + IEmployeeSerializer."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.subpath = []

    def publishTraverse(self, request, name):
        self.subpath.append(name)
        return self

    def __call__(self):
        method = self.request.method.upper()
        # ZCA Dependency Injection lookup (like @Autowired IEmployeeService)
        service = getUtility(IEmployeeService)

        try:
            if not self.subpath:
                if method == "GET":
                    dept = self.request.form.get("dept", "")
                    include_deleted = self.request.form.get("includeDeleted", "").lower() == "true"
                    employees = service.list_employees(
                        self.context, dept=dept, include_deleted=include_deleted
                    )
                    # ZCA Adapter call: IEmployeeSerializer(emp) converts IEmployee -> dict
                    items = [IEmployeeSerializer(emp).to_summary_dict() for emp in employees]
                    return self.json_ok({"items": items, "totalCount": len(items)})

                if method == "POST":
                    try:
                        body = self.read_json_body()
                    except ValueError:
                        return self.json_error("E_INVALID_JSON", "Invalid JSON body.", 400)
                    emp = service.create_employee(self.context, body)
                    return self.json_ok(IEmployeeSerializer(emp).to_dict(), status=201)

                return self.json_error("E_METHOD_NOT_ALLOWED", f"{method} not allowed", 405)

            if len(self.subpath) == 1:
                emp_code = self.subpath[0]
                if method == "GET":
                    emp = service.get_employee(self.context, emp_code)
                    if emp is None:
                        return self.json_error(
                            "E_NOT_FOUND", f"Employee '{emp_code}' was not found.", 404
                        )
                    return self.json_ok(IEmployeeSerializer(emp).to_dict())

                if method == "DELETE":
                    emp = service.delete_employee(self.context, emp_code)
                    return self.json_ok(
                        {
                            "empCode": emp.emp_code,
                            "deletedFlg": emp.deleted_flg,
                            "updatedAt": emp.updated_at,
                        }
                    )

                return self.json_error("E_METHOD_NOT_ALLOWED", f"{method} not allowed", 405)

            return self.json_error("E_INVALID_PATH", "Unsupported path.", 404)

        except ServiceError as err:
            return self.json_error(err.code, err.message, status=err.status)


class AuditLogsApiView(BaseJsonView):
    """GET /api-audit-logs — shows domain events captured by ZCA <subscriber>s."""

    def __call__(self):
        audit = getUtility(IAuditLogUtility)
        entries = audit.list_entries()
        return self.json_ok({"items": entries, "totalCount": len(entries)})
