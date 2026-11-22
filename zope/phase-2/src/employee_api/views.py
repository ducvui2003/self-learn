"""Phase 2 REST API views backed by ZODB (with ACID transactions & Acquisition).

Spring equivalent:
  - Each HTTP request in Zope runs inside an automatic transaction (like @Transactional).
  - Normal return -> Zope commits ZODB changes to var/Data.fs automatically.
  - transaction.abort() or unhandled exception -> Zope rolls back all ZODB changes.
"""

import json

from Products.Five.browser import BrowserView
import transaction
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from .models import Employee, now_jst_iso
from .storage import get_or_create_store


class BaseJsonView(BrowserView):
    """Base helper for consistent Japan-enterprise JSON responses."""

    def read_json_body(self):
        """Parse UTF-8 JSON body from self.request (like @RequestBody in Spring)."""
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
            "error": {
                "code": code,
                "message": message,
            },
            "timestamp": now_jst_iso(),
        }
        return self._write_json(payload, status)

    def _write_json(self, payload, status):
        response = self.request.response
        response.setStatus(status)
        response.setHeader("Content-Type", "application/json; charset=utf-8")
        return json.dumps(payload, ensure_ascii=False, indent=2)


class HealthApiView(BaseJsonView):
    """GET /api-health — reports ZODB store status."""

    def __call__(self):
        store = get_or_create_store(self.context)
        active_count = len(store.list_employees(include_deleted=False))
        total_count = len(store.employees)
        return self.json_ok(
            {
                "service": "zope-phase2-zodb-api",
                "zodbStoreId": store.getId(),
                "companyName": store.company_name,
                "activeEmployees": active_count,
                "totalStoredInZodb": total_count,
            }
        )


@implementer(IPublishTraverse)
class EmployeesApiView(BaseJsonView):
    """ZODB-backed Employee REST API.

    Endpoints:
      GET    /api-employees                          -> list from ZODB OOBTree
      POST   /api-employees                          -> create Employee in ZODB
      POST   /api-employees?simulateError=true       -> demonstrate ACID rollback
      GET    /api-employees/{empCode}                -> get Employee + Acquisition demo
      POST   /api-employees/{empCode}/skills         -> append to PersistentList
      DELETE /api-employees/{empCode}                -> soft delete (deleted_flg=True)
    """

    def __init__(self, context, request):
        super().__init__(context, request)
        self.subpath = []

    def publishTraverse(self, request, name):
        self.subpath.append(name)
        return self

    def __call__(self):
        method = self.request.method.upper()
        store = get_or_create_store(self.context)

        # Collection routes: /api-employees
        if not self.subpath:
            if method == "GET":
                return self._list_employees(store)
            if method == "POST":
                return self._create_employee(store)
            return self.json_error("E_METHOD_NOT_ALLOWED", f"{method} not allowed", 405)

        # Item routes: /api-employees/{empCode}
        if len(self.subpath) == 1:
            emp_code = self.subpath[0]
            if method == "GET":
                return self._get_employee(store, emp_code)
            if method == "DELETE":
                return self._delete_employee(store, emp_code)
            return self.json_error("E_METHOD_NOT_ALLOWED", f"{method} not allowed", 405)

        # Sub-resource route: /api-employees/{empCode}/skills
        if len(self.subpath) == 2 and self.subpath[1] == "skills":
            if method == "POST":
                return self._add_skill(store, self.subpath[0])
            return self.json_error("E_METHOD_NOT_ALLOWED", f"{method} not allowed", 405)

        return self.json_error(
            code="E_INVALID_PATH",
            message="Unsupported path: /" + "/".join(self.subpath),
            status=404,
        )

    def _list_employees(self, store):
        dept = self.request.form.get("dept", "").strip().lower()
        include_deleted = self.request.form.get("includeDeleted", "").lower() == "true"

        employees = store.list_employees(include_deleted=include_deleted)
        if dept:
            employees = [
                emp
                for emp in employees
                if dept in emp.department_en.lower() or dept in emp.department_ja
            ]

        return self.json_ok(
            {
                "items": [emp.to_dict() for emp in employees],
                "totalCount": len(employees),
            }
        )

    def _get_employee(self, store, emp_code):
        emp = store.get_employee(emp_code)
        if emp is None or emp.deleted_flg:
            return self.json_error(
                code="E_NOT_FOUND",
                message=f"Employee '{emp_code}' was not found.",
                status=404,
            )
        # Include Acquisition demo details so we can inspect parent-inherited attrs
        return self.json_ok(emp.to_dict(include_acquisition_info=True))

    def _create_employee(self, store):
        try:
            body = self.read_json_body()
        except ValueError:
            return self.json_error("E_INVALID_JSON", "Request body must be valid JSON.", 400)

        required = ["empCode", "nameEn", "nameJa", "departmentEn", "departmentJa", "role", "email"]
        missing = [f for f in required if not str(body.get(f, "")).strip()]
        if missing:
            return self.json_error(
                code="E_VALIDATION",
                message="Missing required fields: " + ", ".join(missing),
                status=400,
            )

        emp_code = body["empCode"].strip().upper()
        if store.get_employee(emp_code) is not None:
            return self.json_error(
                code="E_DUPLICATE",
                message=f"Employee '{emp_code}' already exists in ZODB.",
                status=409,
            )

        emp = Employee(
            emp_code=emp_code,
            name_en=body["nameEn"].strip(),
            name_ja=body["nameJa"].strip(),
            department_en=body["departmentEn"].strip(),
            department_ja=body["departmentJa"].strip(),
            role=body["role"].strip(),
            email=body["email"].strip(),
            skills=body.get("skills", []),
        )
        store.add_employee(emp)

        # ACID TRANSACTION ROLLBACK DEMO:
        # Like Spring @Transactional rolling back on exception.
        # Notice `store.add_employee(emp)` already mutated the OOBTree above,
        # but calling `transaction.abort()` discards that change completely!
        if self.request.form.get("simulateError", "").lower() == "true":
            transaction.abort()
            return self.json_error(
                code="E_TX_ROLLED_BACK",
                message=f"Simulated error! Transaction aborted — '{emp_code}' was NOT saved to ZODB.",
                status=500,
            )

        # No manual commit needed: Zope commits the transaction automatically on return!
        wrapped_emp = store.get_employee(emp_code)
        return self.json_ok(wrapped_emp.to_dict(include_acquisition_info=True), status=201)

    def _add_skill(self, store, emp_code):
        emp = store.get_employee(emp_code)
        if emp is None or emp.deleted_flg:
            return self.json_error("E_NOT_FOUND", f"Employee '{emp_code}' was not found.", 404)

        try:
            body = self.read_json_body()
        except ValueError:
            return self.json_error("E_INVALID_JSON", "Request body must be valid JSON.", 400)

        skill = str(body.get("skill", "")).strip()
        if not skill:
            return self.json_error("E_VALIDATION", "Field 'skill' is required.", 400)

        # Mutates emp.skills (PersistentList) -> ZODB persists it automatically on commit
        added = emp.add_skill(skill)
        return self.json_ok(
            {
                "empCode": emp.emp_code,
                "skillAdded": added,
                "skills": list(emp.skills),
                "updatedAt": emp.updated_at,
            }
        )

    def _delete_employee(self, store, emp_code):
        emp = store.get_employee(emp_code)
        if emp is None or emp.deleted_flg:
            return self.json_error("E_NOT_FOUND", f"Employee '{emp_code}' was not found.", 404)

        # Soft delete (deleted_flg = True) -> persisted in ZODB automatically
        emp.soft_delete()
        return self.json_ok(
            {
                "empCode": emp.emp_code,
                "deletedFlg": emp.deleted_flg,
                "updatedAt": emp.updated_at,
            }
        )
