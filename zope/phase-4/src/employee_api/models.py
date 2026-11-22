"""ZODB Employee model with optimistic locking (`version`) & soft delete."""

from datetime import datetime, timezone, timedelta

from BTrees.OOBTree import OOBTree
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from persistent.list import PersistentList

JST = timezone(timedelta(hours=9))


def now_jst_iso():
    return datetime.now(JST).isoformat()


class Employee(SimpleItem):
    """Persistent Employee with version counter (like JPA @Version)."""

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

        # Optimistic locking + audit columns
        self.version = 1
        now = now_jst_iso()
        self.created_at = now
        self.created_by = created_by
        self.updated_at = now
        self.updated_by = created_by
        self.deleted_flg = False

    def update_fields(self, data, updated_by="api"):
        for key in ("name_en", "name_ja", "department_en", "department_ja", "role", "email"):
            if key in data:
                setattr(self, key, data[key])
        if "skills" in data:
            self.skills = PersistentList(data["skills"])
        self.version += 1
        self.updated_at = now_jst_iso()
        self.updated_by = updated_by

    def soft_delete(self, updated_by="api"):
        self.deleted_flg = True
        self.version += 1
        self.updated_at = now_jst_iso()
        self.updated_by = updated_by

    def to_dict(self):
        return {
            "empCode": self.emp_code,
            "nameEn": self.name_en,
            "nameJa": self.name_ja,
            "departmentEn": self.department_en,
            "departmentJa": self.department_ja,
            "role": self.role,
            "email": self.email,
            "skills": list(self.skills),
            "version": self.version,
            "deletedFlg": self.deleted_flg,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class EmployeeFolder(Folder):
    meta_type = "EmployeeFolder"

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
