"""ZODB store helper with 5 seed employees (so pagination is easy to test!)."""

from .models import Employee, EmployeeFolder

STORE_ID = "employees_store"


def get_or_create_store(root):
    if STORE_ID not in root.objectIds():
        folder = EmployeeFolder(STORE_ID)
        for emp in _seed_employees():
            folder.add_employee(emp)
        root._setObject(STORE_ID, folder)
    return root[STORE_ID]


def _seed_employees():
    return [
        Employee("EMP-0001", "Kenji Sato", "佐藤 健司", "Sales", "営業部", "Manager", "k.sato@example.co.jp", ["B2B Sales"]),
        Employee("EMP-0002", "Yuki Tanaka", "田中 由紀", "Engineering", "開発部", "Senior Backend Engineer", "y.tanaka@example.co.jp", ["Python", "Zope", "MySQL"]),
        Employee("EMP-0003", "Haruka Suzuki", "鈴木 遥", "HR", "人事部", "HR Specialist", "h.suzuki@example.co.jp", ["Recruiting"]),
        Employee("EMP-0004", "Daiki Takahashi", "高橋 大樹", "Engineering", "開発部", "Tech Lead", "d.takahashi@example.co.jp", ["Java", "Spring Boot", "Zope"]),
        Employee("EMP-0005", "Aoi Watanabe", "渡辺 葵", "Finance", "経理部", "Accountant", "a.watanabe@example.co.jp", ["Accounting", "Excel"]),
    ]
