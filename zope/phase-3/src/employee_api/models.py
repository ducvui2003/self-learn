"""Domain models implementing ZCA interfaces (`@implementer(IEmployee)`).

Notice how clean `Employee` is now compared to Phase 2:
- Serialization (`to_dict`) moved out into a ZCA Adapter (`adapters.py`).
- Business logic moved out into a ZCA Utility (`services.py`).
"""

from datetime import datetime, timezone, timedelta

from BTrees.OOBTree import OOBTree
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from persistent.list import PersistentList
from zope.interface import implementer

from .interfaces import IEmployee

JST = timezone(timedelta(hours=9))


def now_jst_iso():
    """Return current time in JST (+09:00) ISO-8601 format."""
    return datetime.now(JST).isoformat()


@implementer(IEmployee)
class Employee(SimpleItem):
    """Persistent Employee entity implementing IEmployee."""

    meta_type = "Employee"

    def __init__(
        self,
        emp_code,
        name_en,
        name_ja,
        department_en,
        department_ja,
        role,
        email,
        skills=None,
        created_by="system",
    ):
        self.id = emp_code
        self.emp_code = emp_code
        self.name_en = name_en
        self.name_ja = name_ja
        self.department_en = department_en
        self.department_ja = department_ja
        self.role = role
        self.email = email
        self.skills = PersistentList(skills or [])

        now = now_jst_iso()
        self.created_at = now
        self.created_by = created_by
        self.updated_at = now
        self.updated_by = created_by
        self.deleted_flg = False

    def soft_delete(self, updated_by="api"):
        self.deleted_flg = True
        self.updated_at = now_jst_iso()
        self.updated_by = updated_by


class EmployeeFolder(Folder):
    """ZODB Folder storing Employee objects in an OOBTree."""

    meta_type = "EmployeeFolder"
    company_name = "Tokyo Tech Corp (東京テック株式会社)"

    def __init__(self, id="employees_store"):
        super().__init__(id)
        self.employees = OOBTree()

    def get_employee(self, emp_code):
        emp = self.employees.get(emp_code.upper())
        return emp.__of__(self) if emp is not None else None

    def add_employee(self, emp):
        self.employees[emp.emp_code.upper()] = emp

    def list_employees(self, include_deleted=False):
        return [
            emp.__of__(self)
            for emp in self.employees.values()
            if include_deleted or not emp.deleted_flg
        ]
