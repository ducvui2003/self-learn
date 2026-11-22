"""DELETE handler for /@@api-employees/{empCode} (logical soft delete)."""

from ...exceptions import ApiError, NotFoundError
from ...storage import get_or_create_store
from ..dispatcher import BaseMethodHandler


class EmployeeDelete(BaseMethodHandler):
    def handle(self):
        if len(self.subpath) != 1:
            raise ApiError("E_INVALID_PATH", "DELETE requires /@@api-employees/{empCode}.", status=400)

        emp_code = self.subpath[0]
        store = get_or_create_store(self.context)
        emp = store.get_employee(emp_code)
        if emp is None or emp.deleted_flg:
            raise NotFoundError(f"Employee '{emp_code}' was not found.")

        emp.soft_delete()
        return (
            {
                "empCode": emp.emp_code,
                "deletedFlg": emp.deleted_flg,
                "version": emp.version,
                "updatedAt": emp.updated_at,
            },
            200,
        )
