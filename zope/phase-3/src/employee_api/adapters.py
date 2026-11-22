"""ZCA Adapter: adapts IEmployee -> IEmployeeSerializer.

Spring equivalent: Converter<Employee, EmployeeDto> / MapStruct Mapper.
In Zope, once registered via <adapter> in configure.zcml, ANY code can do:
    serializer = IEmployeeSerializer(employee)
    payload = serializer.to_dict()
"""

from zope.component import adapter
from zope.interface import implementer

from .interfaces import IEmployee, IEmployeeSerializer


@adapter(IEmployee)
@implementer(IEmployeeSerializer)
class EmployeeJsonSerializer:
    """Converts an IEmployee domain object into JSON-ready dictionaries."""

    def __init__(self, context):
        # ZCA passes the adapted object (`employee`) into __init__(self, context)
        self.context = context

    def to_dict(self):
        emp = self.context
        return {
            "empCode": emp.emp_code,
            "nameEn": emp.name_en,
            "nameJa": emp.name_ja,
            "departmentEn": emp.department_en,
            "departmentJa": emp.department_ja,
            "role": emp.role,
            "email": emp.email,
            "skills": list(emp.skills),
            "companyName": getattr(emp, "company_name", None),
            "deletedFlg": emp.deleted_flg,
            "createdAt": emp.created_at,
            "updatedAt": emp.updated_at,
        }

    def to_summary_dict(self):
        emp = self.context
        return {
            "empCode": emp.emp_code,
            "nameEn": emp.name_en,
            "nameJa": emp.name_ja,
            "departmentEn": emp.department_en,
            "departmentJa": emp.department_ja,
            "role": emp.role,
            "deletedFlg": emp.deleted_flg,
        }
