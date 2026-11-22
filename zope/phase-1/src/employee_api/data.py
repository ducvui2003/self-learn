"""In-memory Japan-enterprise sample data for Phase 1.

In Phase 2 we will move this data into ZODB, and in Phase 5 into MySQL.
"""

EMPLOYEES = [
    {
        "empCode": "EMP-0001",
        "nameEn": "Kenji Sato",
        "nameJa": "佐藤 健司",
        "departmentEn": "Sales",
        "departmentJa": "営業部",
        "role": "Manager",
        "email": "k.sato@example.co.jp",
        "joinedAt": "2020-04-01T09:00:00+09:00",
    },
    {
        "empCode": "EMP-0002",
        "nameEn": "Yuki Tanaka",
        "nameJa": "田中 由紀",
        "departmentEn": "Engineering",
        "departmentJa": "開発部",
        "role": "Senior Backend Engineer",
        "email": "y.tanaka@example.co.jp",
        "joinedAt": "2022-04-01T09:00:00+09:00",
    },
    {
        "empCode": "EMP-0003",
        "nameEn": "Haruka Suzuki",
        "nameJa": "鈴木 遥",
        "departmentEn": "HR",
        "departmentJa": "人事部",
        "role": "HR Specialist",
        "email": "h.suzuki@example.co.jp",
        "joinedAt": "2023-10-01T09:00:00+09:00",
    },
]
