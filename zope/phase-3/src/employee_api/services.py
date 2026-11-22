"""ZCA Utilities (Spring @Service singleton equivalent).

Registered once in configure.zcml via:
    <utility provides=".interfaces.IEmployeeService" factory=".services.EmployeeService" />

Any view or subscriber can look them up by interface:
    service = getUtility(IEmployeeService)
"""

from collections import deque

from zope.event import notify
from zope.interface import implementer

from .events import EmployeeCreatedEvent, EmployeeDeletedEvent
from .interfaces import IAuditLogUtility, IEmployeeService
from .models import Employee, EmployeeFolder, now_jst_iso

STORE_ID = "employees_store"


class ServiceError(Exception):
    """Domain error with a Japan-enterprise error code and HTTP status."""

    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


@implementer(IAuditLogUtility)
class AuditLogUtility:
    """Singleton Utility holding recent domain event audit records in memory.

    In Phase 5 we will persist audit logs into a MySQL `audit_logs` table!
    """

    def __init__(self):
        self._entries = deque(maxlen=100)

    def record(self, event_type, emp_code, detail):
        self._entries.appendleft(
            {
                "eventType": event_type,
                "empCode": emp_code,
                "detail": detail,
                "recordedAt": now_jst_iso(),
            }
        )

    def list_entries(self, limit=50):
        return list(self._entries)[:limit]


@implementer(IEmployeeService)
class EmployeeService:
    """Singleton Utility implementing employee business logic (like Spring @Service)."""

    def _get_or_create_store(self, root):
        if STORE_ID not in root.objectIds():
            folder = EmployeeFolder(STORE_ID)
            for emp in self._seed_employees():
                folder.add_employee(emp)
            root._setObject(STORE_ID, folder)
        return root[STORE_ID]

    def _seed_employees(self):
        return [
            Employee(
                emp_code="EMP-0001",
                name_en="Kenji Sato",
                name_ja="佐藤 健司",
                department_en="Sales",
                department_ja="営業部",
                role="Manager",
                email="k.sato@example.co.jp",
                skills=["B2B Sales", "Account Management"],
            ),
            Employee(
                emp_code="EMP-0002",
                name_en="Yuki Tanaka",
                name_ja="田中 由紀",
                department_en="Engineering",
                department_ja="開発部",
                role="Senior Backend Engineer",
                email="y.tanaka@example.co.jp",
                skills=["Python", "Zope", "MySQL"],
            ),
            Employee(
                emp_code="EMP-0003",
                name_en="Haruka Suzuki",
                name_ja="鈴木 遥",
                department_en="HR",
                department_ja="人事部",
                role="HR Specialist",
                email="h.suzuki@example.co.jp",
                skills=["Recruiting", "Onboarding"],
            ),
        ]

    def list_employees(self, root, dept="", include_deleted=False):
        store = self._get_or_create_store(root)
        employees = store.list_employees(include_deleted=include_deleted)
        dept_clean = dept.strip().lower()
        if dept_clean:
            employees = [
                emp
                for emp in employees
                if dept_clean in emp.department_en.lower()
                or dept_clean in emp.department_ja
            ]
        return employees

    def get_employee(self, root, emp_code):
        store = self._get_or_create_store(root)
        emp = store.get_employee(emp_code)
        if emp is None or emp.deleted_flg:
            return None
        return emp

    def create_employee(self, root, payload):
        store = self._get_or_create_store(root)

        required = ["empCode", "nameEn", "nameJa", "departmentEn", "departmentJa", "role", "email"]
        missing = [f for f in required if not str(payload.get(f, "")).strip()]
        if missing:
            raise ServiceError(
                code="E_VALIDATION",
                message="Missing required fields: " + ", ".join(missing),
                status=400,
            )

        emp_code = payload["empCode"].strip().upper()
        if store.get_employee(emp_code) is not None:
            raise ServiceError(
                code="E_DUPLICATE",
                message=f"Employee '{emp_code}' already exists.",
                status=409,
            )

        emp = Employee(
            emp_code=emp_code,
            name_en=payload["nameEn"].strip(),
            name_ja=payload["nameJa"].strip(),
            department_en=payload["departmentEn"].strip(),
            department_ja=payload["departmentJa"].strip(),
            role=payload["role"].strip(),
            email=payload["email"].strip(),
            skills=payload.get("skills", []),
        )
        store.add_employee(emp)
        wrapped = store.get_employee(emp_code)

        # Publish ZCA domain event (Spring: applicationEventPublisher.publishEvent(...))
        notify(EmployeeCreatedEvent(wrapped))
        return wrapped

    def delete_employee(self, root, emp_code):
        store = self._get_or_create_store(root)
        emp = store.get_employee(emp_code)
        if emp is None or emp.deleted_flg:
            raise ServiceError(
                code="E_NOT_FOUND",
                message=f"Employee '{emp_code}' was not found.",
                status=404,
            )

        emp.soft_delete()
        # Publish ZCA domain event -> triggers subscribers.on_employee_deleted
        notify(EmployeeDeletedEvent(emp))
        return emp
