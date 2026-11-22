"""ZODB storage helper: initializes EmployeeFolder inside Zope root if missing.

In Zope, the root object (`/`) is already stored in ZODB (`var/Data.fs`).
When we call `root._setObject("employees_store", folder)`, Zope saves it
automatically when the current HTTP request transaction commits.
"""

from .models import Employee, EmployeeFolder

STORE_ID = "employees_store"


def get_or_create_store(root):
    """Return the persistent EmployeeFolder from ZODB, seeding initial data once."""
    if STORE_ID not in root.objectIds():
        folder = EmployeeFolder(STORE_ID)
        _seed_initial_employees(folder)
        root._setObject(STORE_ID, folder)

    # Accessing via root[STORE_ID] returns the folder wrapped in Acquisition.
    return root[STORE_ID]


def _seed_initial_employees(folder):
    """Seed realistic Japan-enterprise employees on first boot."""
    initial_data = [
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
    for emp in initial_data:
        folder.add_employee(emp)
