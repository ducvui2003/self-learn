"""Phase 5 REST API Views: Role-Based Security + MySQL (SQLAlchemy + zope.sqlalchemy).

Endpoints:
  GET    /@@api-health            (Public — initializes demo users & DB, shows DB backend)
  GET    /@@api-me                (Authenticated — shows current Zope user & roles)
  GET    /@@api-employees         (Roles: Viewer or HRManager)
  POST   /@@api-employees         (Roles: HRManager only; ?simulateError=true tests SQL rollback!)
  DELETE /@@api-employees/{code}  (Roles: HRManager only; soft deletes in SQL + writes audit_logs)
  GET    /@@api-audit-logs        (Roles: HRManager only; reads SQL audit_logs table)
"""

import json

from Products.Five.browser import BrowserView
import transaction
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from .db import AuditLogRecord, EmployeeRecord, get_database_url, get_session, now_jst_iso
from .security import ensure_demo_users, get_current_user_info, has_any_role


class BaseSecuredJsonView(BrowserView):
    """Base REST view with Zope Security role checks + JSON envelope."""

    def read_json_body(self):
        raw = self.request.get("BODY", b"")
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        if not raw or not raw.strip():
            return {}
        return json.loads(raw)

    def require_auth(self, allowed_roles=None):
        """Return `(username, roles)` or `(None, error_response_str)`.

        Spring Security equivalent: @PreAuthorize("hasAnyRole('HR_MANAGER', 'VIEWER')").
        """
        username, roles, is_anon = get_current_user_info(self.context)
        if is_anon:
            self.request.response.setHeader("WWW-Authenticate", 'Basic realm="Zope HR API"')
            return None, self.json_error(
                code="E_UNAUTHORIZED",
                message="Authentication required. Send Basic Auth (e.g. hr_manager:hr123 or viewer:viewer123).",
                status=401,
            )

        if allowed_roles and not has_any_role(roles, allowed_roles):
            return None, self.json_error(
                code="E_FORBIDDEN",
                message=f"User '{username}' lacks required role: {', '.join(allowed_roles)}.",
                status=403,
            )

        return username, None

    def json_ok(self, data, status=200):
        payload = {"status": "ok", "data": data, "timestamp": now_jst_iso()}
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


class HealthApiView(BaseSecuredJsonView):
    """GET /@@api-health — public health check + initializes demo Zope users & SQL DB."""

    def __call__(self):
        ensure_demo_users(self.context)
        session = get_session()
        active_count = (
            session.query(EmployeeRecord).filter(EmployeeRecord.deleted_flg.is_(False)).count()
        )
        db_url = get_database_url()
        backend = "MySQL (PyMySQL)" if db_url.startswith("mysql") else "SQLite (local fallback)"
        return self.json_ok(
            {
                "service": "zope-phase5-security-mysql-api",
                "databaseBackend": backend,
                "activeEmployees": active_count,
                "demoUsers": ["hr_manager:hr123 (HRManager)", "viewer:viewer123 (Viewer)"],
            }
        )


class MeApiView(BaseSecuredJsonView):
    """GET /@@api-me — shows currently authenticated Zope user and roles."""

    def __call__(self):
        ensure_demo_users(self.context)
        username, err = self.require_auth()
        if err is not None:
            return err
        _, roles, _ = get_current_user_info(self.context)
        return self.json_ok({"username": username, "roles": roles})


@implementer(IPublishTraverse)
class EmployeesSqlApiView(BaseSecuredJsonView):
    """Role-protected Employee REST API backed by MySQL/SQLAlchemy + zope.sqlalchemy."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.subpath = []

    def publishTraverse(self, request, name):
        self.subpath.append(name)
        return self

    def __call__(self):
        ensure_demo_users(self.context)
        method = self.request.method.upper()

        if not self.subpath:
            if method == "GET":
                _, err = self.require_auth(allowed_roles=["Viewer", "HRManager"])
                return err or self._list_employees()
            if method == "POST":
                actor, err = self.require_auth(allowed_roles=["HRManager"])
                return err or self._create_employee(actor)
            return self.json_error("E_METHOD_NOT_ALLOWED", f"{method} not allowed", 405)

        if len(self.subpath) == 1:
            emp_code = self.subpath[0].upper()
            if method == "GET":
                _, err = self.require_auth(allowed_roles=["Viewer", "HRManager"])
                return err or self._get_employee(emp_code)
            if method == "DELETE":
                actor, err = self.require_auth(allowed_roles=["HRManager"])
                return err or self._delete_employee(emp_code, actor)
            return self.json_error("E_METHOD_NOT_ALLOWED", f"{method} not allowed", 405)

        return self.json_error("E_INVALID_PATH", "Unsupported path.", 404)

    def _list_employees(self):
        session = get_session()
        dept = self.request.form.get("dept", "").strip()
        query = session.query(EmployeeRecord).filter(EmployeeRecord.deleted_flg.is_(False))
        if dept:
            query = query.filter(
                (EmployeeRecord.department_en.ilike(f"%{dept}%"))
                | (EmployeeRecord.department_ja.like(f"%{dept}%"))
            )
        rows = query.order_by(EmployeeRecord.emp_code.asc()).all()
        return self.json_ok({"items": [r.to_dict() for r in rows], "totalCount": len(rows)})

    def _get_employee(self, emp_code):
        session = get_session()
        row = (
            session.query(EmployeeRecord)
            .filter(EmployeeRecord.emp_code == emp_code, EmployeeRecord.deleted_flg.is_(False))
            .first()
        )
        if row is None:
            return self.json_error("E_NOT_FOUND", f"Employee '{emp_code}' was not found.", 404)
        return self.json_ok(row.to_dict())

    def _create_employee(self, actor):
        try:
            body = self.read_json_body()
        except ValueError:
            return self.json_error("E_INVALID_JSON", "Request body must be valid JSON.", 400)

        required = ["empCode", "nameEn", "nameJa", "departmentEn", "departmentJa", "role", "email"]
        missing = [f for f in required if not str(body.get(f, "")).strip()]
        if missing:
            return self.json_error("E_VALIDATION", "Missing fields: " + ", ".join(missing), 400)

        emp_code = body["empCode"].strip().upper()
        session = get_session()
        if session.query(EmployeeRecord).filter(EmployeeRecord.emp_code == emp_code).first():
            return self.json_error("E_DUPLICATE", f"Employee '{emp_code}' already exists.", 409)

        now = now_jst_iso()
        emp = EmployeeRecord(
            emp_code=emp_code,
            name_en=body["nameEn"].strip(),
            name_ja=body["nameJa"].strip(),
            department_en=body["departmentEn"].strip(),
            department_ja=body["departmentJa"].strip(),
            role=body["role"].strip(),
            email=body["email"].strip().lower(),
            version=1,
            deleted_flg=False,
            created_at=now,
            created_by=actor,
            updated_at=now,
            updated_by=actor,
        )
        session.add(emp)
        session.add(
            AuditLogRecord(
                action="EMPLOYEE_CREATED",
                emp_code=emp_code,
                actor=actor,
                detail=f"Created {emp.name_en} ({emp.name_ja})",
                created_at=now,
            )
        )
        # Flush sends INSERT to SQL DB inside the current Zope transaction
        session.flush()

        # TWO-PHASE TRANSACTION ROLLBACK DEMO:
        # Both `employees` AND `audit_logs` inserts are rolled back together!
        if self.request.form.get("simulateError", "").lower() == "true":
            transaction.abort()
            return self.json_error(
                code="E_SQL_TX_ROLLED_BACK",
                message=f"Simulated error! Zope aborted transaction — '{emp_code}' and its audit log were rolled back.",
                status=500,
            )

        # No session.commit() needed! zope.sqlalchemy commits automatically when Zope finishes.
        return self.json_ok(emp.to_dict(), status=201)

    def _delete_employee(self, emp_code, actor):
        session = get_session()
        row = (
            session.query(EmployeeRecord)
            .filter(EmployeeRecord.emp_code == emp_code, EmployeeRecord.deleted_flg.is_(False))
            .first()
        )
        if row is None:
            return self.json_error("E_NOT_FOUND", f"Employee '{emp_code}' was not found.", 404)

        now = now_jst_iso()
        row.deleted_flg = True
        row.version += 1
        row.updated_at = now
        row.updated_by = actor
        session.add(
            AuditLogRecord(
                action="EMPLOYEE_DELETED",
                emp_code=emp_code,
                actor=actor,
                detail=f"Soft-deleted {row.name_en} ({row.name_ja})",
                created_at=now,
            )
        )
        session.flush()
        return self.json_ok(row.to_dict())


class AuditLogsSqlApiView(BaseSecuredJsonView):
    """GET /@@api-audit-logs — HRManager only, reads SQL `audit_logs` table."""

    def __call__(self):
        ensure_demo_users(self.context)
        _, err = self.require_auth(allowed_roles=["HRManager"])
        if err is not None:
            return err

        session = get_session()
        rows = session.query(AuditLogRecord).order_by(AuditLogRecord.id.desc()).limit(50).all()
        return self.json_ok({"items": [r.to_dict() for r in rows], "totalCount": len(rows)})
