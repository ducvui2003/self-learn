"""ZCA Event Subscribers (Spring @EventListener equivalent).

Registered in configure.zcml via <subscriber for="..." handler="..." />.
When EmployeeService calls `zope.event.notify(EmployeeCreatedEvent(emp))`,
Zope automatically invokes `on_employee_created` — completely decoupled from the service!
"""

import logging

from zope.component import getUtility

from .interfaces import IAuditLogUtility

logger = logging.getLogger("employee_api.audit")


def on_employee_created(event):
    """Subscriber called automatically whenever IEmployeeCreatedEvent is fired."""
    emp = event.employee
    detail = f"Created {emp.name_en} ({emp.name_ja}) in {emp.department_en} ({emp.department_ja})"
    logger.info("[AUDIT] EMPLOYEE_CREATED %s: %s", emp.emp_code, detail)

    audit = getUtility(IAuditLogUtility)
    audit.record("EMPLOYEE_CREATED", emp.emp_code, detail)


def on_employee_deleted(event):
    """Subscriber called automatically whenever IEmployeeDeletedEvent is fired."""
    emp = event.employee
    detail = f"Soft-deleted {emp.name_en} ({emp.name_ja})"
    logger.info("[AUDIT] EMPLOYEE_DELETED %s: %s", emp.emp_code, detail)

    audit = getUtility(IAuditLogUtility)
    audit.record("EMPLOYEE_DELETED", emp.emp_code, detail)
