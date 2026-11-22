"""PUT handler for /@@api-employees/{empCode} (full update + optimistic locking)."""

from ...exceptions import ApiError, ConflictError, NotFoundError
from ...schemas import validate_put_employee
from ...storage import get_or_create_store
from ..dispatcher import BaseMethodHandler


class EmployeePut(BaseMethodHandler):
    def handle(self):
        if len(self.subpath) != 1:
            raise ApiError("E_INVALID_PATH", "PUT requires /@@api-employees/{empCode}.", status=400)

        emp_code = self.subpath[0]
        store = get_or_create_store(self.context)
        emp = store.get_employee(emp_code)
        if emp is None or emp.deleted_flg:
            raise NotFoundError(f"Employee '{emp_code}' was not found.")

        body = self.read_json_body()
        data = validate_put_employee(body)

        # Optimistic locking check (like JPA @Version)
        if data["version"] != emp.version:
            raise ConflictError(
                "E_VERSION_CONFLICT",
                f"Version mismatch for '{emp.emp_code}': expected {emp.version}, got {data['version']}.",
            )

        emp.update_fields(data)
        return emp.to_dict(), 200
