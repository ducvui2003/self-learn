"""ZODB B-Tree Catalog Index (how Products.ZCatalog FieldIndex & KeywordIndex work).

Why indexing matters in ZODB:
- Scanning every Employee in a folder is O(N) — slow when you have 50,000 objects.
- A ZODB Catalog Index (`OOBTree` -> `OOTreeSet`) gives O(log N) indexed search by
  department (`by_dept`, like FieldIndex) and skill (`by_skill`, like KeywordIndex),
  without loading every Employee object from Data.fs!
"""

from datetime import datetime, timezone, timedelta

from BTrees.OOBTree import OOBTree, OOTreeSet, intersection
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from persistent.list import PersistentList

JST = timezone(timedelta(hours=9))
STORE_ID = "indexed_employees_store"


def now_jst_iso():
    return datetime.now(JST).isoformat()


class Employee(SimpleItem):
    meta_type = "Employee"

    def __init__(self, emp_code, name_en, name_ja, department_en, department_ja, role, skills=None):
        self.id = emp_code
        self.emp_code = emp_code
        self.name_en = name_en
        self.name_ja = name_ja
        self.department_en = department_en
        self.department_ja = department_ja
        self.role = role
        self.skills = PersistentList(skills or [])
        self.deleted_flg = False
        self.updated_at = now_jst_iso()

    def to_dict(self):
        return {
            "empCode": self.emp_code,
            "nameEn": self.name_en,
            "nameJa": self.name_ja,
            "departmentEn": self.department_en,
            "departmentJa": self.department_ja,
            "role": self.role,
            "skills": list(self.skills),
            "deletedFlg": self.deleted_flg,
            "updatedAt": self.updated_at,
        }


class IndexedEmployeeFolder(Folder):
    """ZODB Folder with built-in B-Tree indexes (FieldIndex + KeywordIndex pattern)."""

    meta_type = "IndexedEmployeeFolder"

    def __init__(self, id=STORE_ID):
        super().__init__(id)
        self.employees = OOBTree()
        # Inverted indexes (exact same structure used inside Products.ZCatalog):
        #   by_dept["engineering"] -> OOTreeSet({"EMP-0002", "EMP-0004"})
        #   by_skill["mysql"]      -> OOTreeSet({"EMP-0002"})
        self.by_dept = OOBTree()
        self.by_skill = OOBTree()

    def index_employee(self, emp):
        """Save employee and update both B-Tree indexes."""
        code = emp.emp_code.upper()
        self.employees[code] = emp

        dept_key = emp.department_en.lower()
        if dept_key not in self.by_dept:
            self.by_dept[dept_key] = OOTreeSet()
        self.by_dept[dept_key].insert(code)

        for skill in emp.skills:
            skill_key = skill.strip().lower()
            if not skill_key:
                continue
            if skill_key not in self.by_skill:
                self.by_skill[skill_key] = OOTreeSet()
            self.by_skill[skill_key].insert(code)

    def search_indexed(self, dept="", skill=""):
        """Fast O(log N) catalog lookup using B-Tree set intersection (no full table scan!)."""
        dept_key = dept.strip().lower()
        skill_key = skill.strip().lower()

        if dept_key and skill_key:
            dept_ids = self.by_dept.get(dept_key, OOTreeSet())
            skill_ids = self.by_skill.get(skill_key, OOTreeSet())
            matched_codes = intersection(dept_ids, skill_ids)
        elif dept_key:
            matched_codes = self.by_dept.get(dept_key, OOTreeSet())
        elif skill_key:
            matched_codes = self.by_skill.get(skill_key, OOTreeSet())
        else:
            matched_codes = self.employees.keys()

        result = []
        for code in matched_codes:
            emp = self.employees.get(code)
            if emp is not None and not emp.deleted_flg:
                result.append(emp.__of__(self))
        return result


def get_or_create_indexed_store(root):
    if STORE_ID not in root.objectIds():
        folder = IndexedEmployeeFolder(STORE_ID)
        seeds = [
            Employee("EMP-0001", "Kenji Sato", "佐藤 健司", "Sales", "営業部", "Manager", ["B2B", "CRM"]),
            Employee("EMP-0002", "Yuki Tanaka", "田中 由紀", "Engineering", "開発部", "Senior Backend Engineer", ["Python", "Zope", "MySQL"]),
            Employee("EMP-0003", "Haruka Suzuki", "鈴木 遥", "HR", "人事部", "HR Specialist", ["Recruiting", "Onboarding"]),
            Employee("EMP-0004", "Daiki Takahashi", "高橋 大樹", "Engineering", "開発部", "Tech Lead", ["Java", "Spring", "MySQL"]),
        ]
        for emp in seeds:
            folder.index_employee(emp)
        root._setObject(STORE_ID, folder)
    return root[STORE_ID]
