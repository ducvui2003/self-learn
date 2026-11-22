"""ZCA Interfaces (contracts) — Java `interface` equivalent.

In Zope Component Architecture (ZCA), interfaces are the glue for Dependency Injection:
- Classes declare `@implementer(IEmployeeService)` (like `implements EmployeeService`).
- Views look up services by interface: `getUtility(IEmployeeService)` (like `@Autowired`).
- Adapters convert one interface into another: `IEmployeeSerializer(emp)`.
"""

from zope.interface import Attribute, Interface


class IEmployee(Interface):
    """Contract for an Employee domain model."""

    emp_code = Attribute("Unique employee code, e.g. EMP-0001")
    name_en = Attribute("English full name")
    name_ja = Attribute("Japanese full name")
    department_en = Attribute("English department name")
    department_ja = Attribute("Japanese department name")
    role = Attribute("Job title / role")
    email = Attribute("Work email")
    skills = Attribute("PersistentList of skill strings")
    deleted_flg = Attribute("Logical delete flag (bool)")


class IEmployeeSerializer(Interface):
    """Adapter contract: converts an IEmployee object into a JSON dict.

    Spring equivalent: Converter<Employee, EmployeeDto> or MapStruct mapper.
    """

    def to_dict():
        """Return full employee dictionary for JSON response."""

    def to_summary_dict():
        """Return lightweight summary dictionary for list responses."""


class IEmployeeService(Interface):
    """Utility contract: business logic for managing employees.

    Spring equivalent: @Service interface EmployeeService.
    """

    def list_employees(root, dept="", include_deleted=False):
        """Return list of Employee objects."""

    def get_employee(root, emp_code):
        """Return active Employee object or None."""

    def create_employee(root, payload):
        """Create and persist a new Employee, firing IEmployeeCreatedEvent."""

    def delete_employee(root, emp_code):
        """Soft-delete an Employee, firing IEmployeeDeletedEvent."""


class IAuditLogUtility(Interface):
    """Utility contract: stores domain event audit logs.

    Spring equivalent: @Service AuditLogService.
    """

    def record(event_type, emp_code, detail):
        """Record an audit entry."""

    def list_entries(limit=50):
        """Return recent audit entries (newest first)."""


class IEmployeeEvent(Interface):
    """Base interface for employee domain events (Spring ApplicationEvent equivalent)."""

    employee = Attribute("The affected IEmployee object")
    occurred_at = Attribute("ISO-8601 JST timestamp")


class IEmployeeCreatedEvent(IEmployeeEvent):
    """Fired when a new employee is created."""


class IEmployeeDeletedEvent(IEmployeeEvent):
    """Fired when an employee is soft-deleted."""
