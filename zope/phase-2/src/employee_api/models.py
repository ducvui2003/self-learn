"""Phase 2 ZODB Persistent Models (Employee & EmployeeFolder).

Spring / JPA equivalent:
  - SimpleItem / Persistent  ≈ @Entity (saved directly as Python objects, no SQL table)
  - OOBTree                  ≈ B-Tree indexed table / Map<String, Employee>
  - PersistentList           ≈ Tracked collection so ZODB detects .append() changes
  - Acquisition.Implicit     ≈ No Spring equivalent (child inherits attrs from parent folder)
"""

from datetime import datetime, timezone, timedelta

from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from persistent.list import PersistentList

JST = timezone(timedelta(hours=9))


def now_jst_iso():
    """Return current time in JST (+09:00) ISO-8601 format."""
    return datetime.now(JST).isoformat()


class Employee(SimpleItem):
    """A persistent Employee object stored inside ZODB.

    Inheriting from OFS.SimpleItem.SimpleItem gives us:
      1. persistent.Persistent  -> ZODB automatically tracks attribute assignments.
      2. Acquisition.Implicit   -> Child can inherit attributes from its parent folder.
      3. ZMI compatibility      -> Visible/inspectable in Zope's object tree.
    """

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

        # PITFALL PREVENTION:
        # If we used a plain Python list (`self.skills = []`), calling
        # `emp.skills.append("Zope")` would NOT mark `emp` as modified in ZODB!
        # Using PersistentList automatically notifies ZODB on .append() / .remove().
        self.skills = PersistentList(skills or [])

        # Japan-enterprise audit & soft-delete fields
        now = now_jst_iso()
        self.created_at = now
        self.created_by = created_by
        self.updated_at = now
        self.updated_by = created_by
        self.deleted_flg = False

    def add_skill(self, skill_name, updated_by="api"):
        """Add a skill safely using PersistentList (ZODB tracks this change)."""
        if skill_name not in self.skills:
            self.skills.append(skill_name)
            self.updated_at = now_jst_iso()
            self.updated_by = updated_by
            return True
        return False

    def soft_delete(self, updated_by="api"):
        """Mark employee as logically deleted (Japan-enterprise soft delete)."""
        self.deleted_flg = True
        self.updated_at = now_jst_iso()
        self.updated_by = updated_by

    def to_dict(self, include_acquisition_info=False):
        """Serialize this ZODB object to a JSON-friendly dict."""
        data = {
            "empCode": self.emp_code,
            "nameEn": self.name_en,
            "nameJa": self.name_ja,
            "departmentEn": self.department_en,
            "departmentJa": self.department_ja,
            "role": self.role,
            "email": self.email,
            "skills": list(self.skills),
            "deletedFlg": self.deleted_flg,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }

        if include_acquisition_info:
            # ACQUISITION DEMO:
            # `company_name` is defined ONLY on the parent EmployeeFolder, NOT on Employee.
            # 1. `getattr(self, "company_name", None)` walks up to EmployeeFolder via Acquisition.
            # 2. `hasattr(aq_base(self), "company_name")` strips Acquisition and checks ONLY
            #    this Employee's own attributes -> returns False!
            data["acquisitionDemo"] = {
                "acquiredCompanyName": getattr(self, "company_name", None),
                "acquiredOfficeLocation": getattr(self, "office_location", None),
                "hasOwnCompanyNameAttr": hasattr(aq_base(self), "company_name"),
            }

        return data


class EmployeeFolder(Folder):
    """A persistent ZODB Folder storing Employee objects in an OOBTree.

    Why OOBTree instead of a plain Python dict?
    - A plain dict loads ALL entries into memory at once and rewrites the whole dict on change.
    - An OOBTree (Object-key -> Object-value B-Tree) loads only the buckets it needs,
      scaling cleanly to tens of thousands of objects (like a B-Tree index in MySQL).
    """

    meta_type = "EmployeeFolder"

    # Folder-level attributes — child Employee objects inherit these via Acquisition!
    company_name = "Tokyo Tech Corp (東京テック株式会社)"
    office_location = "Minato-ku, Tokyo (東京都港区)"

    def __init__(self, id="employees_store"):
        super().__init__(id)
        self.employees = OOBTree()

    def get_employee(self, emp_code):
        """Fetch an Employee and wrap it in this folder's Acquisition context."""
        emp = self.employees.get(emp_code.upper())
        if emp is None:
            return None
        # Wrap with `.__of__(self)` so `emp` can acquire `company_name` from this folder.
        return emp.__of__(self)

    def add_employee(self, emp):
        """Store an Employee in the OOBTree."""
        self.employees[emp.emp_code.upper()] = emp

    def list_employees(self, include_deleted=False):
        """Return all employees wrapped in Acquisition context."""
        result = []
        for emp in self.employees.values():
            if not include_deleted and emp.deleted_flg:
                continue
            result.append(emp.__of__(self))
        return result
