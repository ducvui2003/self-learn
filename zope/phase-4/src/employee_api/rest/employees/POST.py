"""POST handler for /@@api-employees (create with strict field validation)."""

from ...exceptions import ApiError, ConflictError
from ...models import Employee
from ...schemas import validate_create_employee
from ...storage import get_or_create_store
from ..dispatcher import BaseMethodHandler


class EmployeePost(BaseMethodHandler):
    def handle(self):
        if self.subpath:
            raise ApiError("E_INVALID_PATH", "POST is only allowed on /@@api-employees.", status=405)

        body = self.read_json_body()
        data = validate_create_employee(body)

        store = get_or_create_store(self.context)
        if store.get_employee(data["emp_code"]) is not None:
            raise ConflictError("E_DUPLICATE", f"Employee '{data['emp_code']}' already exists.")

        emp = Employee(**data)
        store.add_employee(emp)
        return store.get_employee(data["emp_code"]).to_dict(), 201
