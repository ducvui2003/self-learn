"""Custom Zope Domain Events (Spring ApplicationEvent equivalent)."""

from zope.interface import implementer

from .interfaces import IEmployeeCreatedEvent, IEmployeeDeletedEvent
from .models import now_jst_iso


@implementer(IEmployeeCreatedEvent)
class EmployeeCreatedEvent:
    """Published via zope.event.notify(...) when an employee is created."""

    def __init__(self, employee):
        self.employee = employee
        self.occurred_at = now_jst_iso()


@implementer(IEmployeeDeletedEvent)
class EmployeeDeletedEvent:
    """Published via zope.event.notify(...) when an employee is soft-deleted."""

    def __init__(self, employee):
        self.employee = employee
        self.occurred_at = now_jst_iso()
