"""Employee REST endpoint wiring GET.py, POST.py, PUT.py, PATCH.py, DELETE.py."""

from ..dispatcher import RestDispatcherView
from .DELETE import EmployeeDelete
from .GET import EmployeeGet
from .PATCH import EmployeePatch
from .POST import EmployeePost
from .PUT import EmployeePut


class EmployeesRestView(RestDispatcherView):
    """Registered in configure.zcml as `name="api-employees"`.

    Automatically dispatches each HTTP method to its dedicated file:
      GET    -> rest/employees/GET.py
      POST   -> rest/employees/POST.py
      PUT    -> rest/employees/PUT.py
      PATCH  -> rest/employees/PATCH.py
      DELETE -> rest/employees/DELETE.py
    """

    handlers = {
        "GET": EmployeeGet,
        "POST": EmployeePost,
        "PUT": EmployeePut,
        "PATCH": EmployeePatch,
        "DELETE": EmployeeDelete,
    }
