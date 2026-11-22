"""GET handler for /@@api-employees and /@@api-employees/{empCode}.

Supports:
  - Search keyword: ?q=tanaka (matches empCode, nameEn, nameJa, role, department)
  - Department filter: ?dept=Engineering
  - Sorting: ?sort=empCode|nameEn|departmentEn & ?order=asc|desc
  - Pagination: ?page=1&size=2
  - Global 500 demo: ?crash=true (proves RestDispatcherView returns JSON, not HTML!)
"""

import math

from ...exceptions import ApiError, NotFoundError
from ...storage import get_or_create_store
from ..dispatcher import BaseMethodHandler

SORT_FIELDS = {
    "empCode": lambda e: e.emp_code,
    "nameEn": lambda e: e.name_en.lower(),
    "departmentEn": lambda e: e.department_en.lower(),
}


class EmployeeGet(BaseMethodHandler):
    def handle(self):
        # Demo: trigger an unexpected exception to prove global JSON 500 handling
        if self.query_param("crash").lower() == "true":
            raise RuntimeError("Simulated unexpected database outage!")

        store = get_or_create_store(self.context)

        # GET /@@api-employees/{empCode}
        if len(self.subpath) == 1:
            emp_code = self.subpath[0]
            emp = store.get_employee(emp_code)
            if emp is None or emp.deleted_flg:
                raise NotFoundError(f"Employee '{emp_code}' was not found.")
            return emp.to_dict(), 200

        if len(self.subpath) > 1:
            raise ApiError("E_INVALID_PATH", "Unsupported path.", status=404)

        # GET /@@api-employees (search + filter + sort + paginate)
        q = self.query_param("q").lower()
        dept = self.query_param("dept").lower()
        sort_key = self.query_param("sort", "empCode")
        order = self.query_param("order", "asc").lower()
        page = self.query_int("page", default=1, min_val=1, max_val=1000)
        size = self.query_int("size", default=10, min_val=1, max_val=100)

        if sort_key not in SORT_FIELDS:
            raise ApiError(
                "E_VALIDATION",
                f"Invalid sort field '{sort_key}'. Allowed: {', '.join(SORT_FIELDS.keys())}.",
                status=400,
            )

        employees = store.list_employees(include_deleted=False)

        if dept:
            employees = [
                e for e in employees
                if dept in e.department_en.lower() or dept in e.department_ja
            ]

        if q:
            employees = [
                e for e in employees
                if q in e.emp_code.lower()
                or q in e.name_en.lower()
                or q in e.name_ja
                or q in e.role.lower()
                or q in e.department_en.lower()
                or q in e.department_ja
            ]

        employees.sort(key=SORT_FIELDS[sort_key], reverse=(order == "desc"))

        total_count = len(employees)
        total_pages = max(1, math.ceil(total_count / size))
        start = (page - 1) * size
        page_items = employees[start : start + size]

        return (
            {
                "items": [e.to_dict() for e in page_items],
                "pagination": {
                    "page": page,
                    "size": size,
                    "totalCount": total_count,
                    "totalPages": total_pages,
                },
            },
            200,
        )
