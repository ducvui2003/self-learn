# Phase 3 — ZCA (Zope Component Architecture) & Layered REST API

Goal: master **ZCA** (`zope.interface`, `zope.component`, `zope.event`, `configure.zcml`) — Zope's equivalent to **Java Spring's Dependency Injection / IoC Container** — and refactor our REST API into clean enterprise layers.

---

## 1. ZCA vs Java Spring DI (Mental-Model Mapping)

If you know Spring Boot DI, ZCA maps almost 1-to-1:

| Concept | Java Spring | Zope 5 (ZCA) |
| :--- | :--- | :--- |
| Contract / Interface | `public interface EmployeeService` | `class IEmployeeService(Interface):` (`zope.interface`) |
| Implement contract | `class EmployeeServiceImpl implements EmployeeService` | `@implementer(IEmployeeService)` |
| Service singleton | `@Service` / `@Bean` | **Utility** (`<utility provides="..." factory="..." />`) |
| Inject / lookup service | `@Autowired EmployeeService` | `getUtility(IEmployeeService)` (or `queryUtility(...)`) |
| Converter / Mapper | `Converter<Employee, EmployeeDto>` / MapStruct | **Adapter** (`<adapter for="IEmployee" provides="IEmployeeSerializer" ... />`) |
| Use converter | `mapper.toDto(emp)` | `IEmployeeSerializer(emp).to_dict()` |
| Publish domain event | `applicationEventPublisher.publishEvent(event)` | `zope.event.notify(EmployeeCreatedEvent(emp))` |
| Listen to event | `@EventListener` | **Subscriber** (`<subscriber for="IEmployeeCreatedEvent" handler="..." />`) |
| Wiring configuration | `@Configuration` / `applicationContext.xml` | `configure.zcml` |

---

## 2. The 4 Building Blocks of ZCA

### A. Interfaces (`interfaces.py`)
Python does not enforce interfaces at compile time like Java. Zope's `zope.interface` gives us explicit contracts (`IEmployee`, `IEmployeeService`, `IEmployeeSerializer`) that ZCA uses as **lookup keys** in its component registry.

### B. Utilities (`services.py`) — Like Spring `@Service`
A **Utility** is a singleton service that does **not** wrap a specific domain object:
```xml
<!-- configure.zcml -->
<utility provides=".interfaces.IEmployeeService" factory=".services.EmployeeService" />
```
```python
# views.py
service = getUtility(IEmployeeService)   # Looks up the singleton registered in ZCML
```
*(You can also register **named utilities** with `name="mysql"` vs `name="zodb"` and call `getUtility(IEmployeeService, name="mysql")` — just like Spring `@Qualifier("mysql")`!)*

### C. Adapters (`adapters.py`) — Like Spring `Converter` / Decorator
An **Adapter** wraps a specific object (`IEmployee`) and adds a new capability (`IEmployeeSerializer`) **without bloating the model class**:
```xml
<!-- configure.zcml -->
<adapter
    for=".interfaces.IEmployee"
    provides=".interfaces.IEmployeeSerializer"
    factory=".adapters.EmployeeJsonSerializer"
    />
```
```python
# views.py — super clean!
dto = IEmployeeSerializer(emp).to_dict()
```
*(Note: A `BrowserView` is actually a **Multi-Adapter** adapting `(context, request)`!)*

### D. Events & Subscribers (`events.py` + `subscribers.py`) — Like Spring `@EventListener`
When `EmployeeService.create_employee()` creates an employee, it does **not** directly call `AuditLogUtility`. Instead, it fires an event:
```python
notify(EmployeeCreatedEvent(emp))
```
Any number of `<subscriber>` handlers registered for `IEmployeeCreatedEvent` run automatically (audit logging, sending email, updating search index) — keeping business logic decoupled!

---

## 3. Clean Layered Architecture (Japan-Enterprise Style)

Compare how Phase 3 separates responsibilities cleanly:

```text
HTTP Request
  -> views.py        (Controller: parse HTTP, call service, adapt to JSON)
  -> services.py     (Service Utility: business rules, validation, fire events)
  -> models.py       (Domain Entity / ZODB storage)
  -> adapters.py     (DTO Serializer: IEmployee -> JSON dict)
  -> subscribers.py  (Side effects: audit logging triggered by domain events)
```

---

## 4. Common Pitfalls

1. **`ComponentLookupError` at runtime:** Means you forgot to register `<utility>` or `<adapter>` in `configure.zcml`, OR forgot `@implementer(IEmployee)` on the model class.
   - Tip: Use `queryUtility(IFoo)` instead of `getUtility(IFoo)` if a utility is optional (`queryUtility` returns `None` instead of raising `ComponentLookupError`).
2. **Storing request-specific state on a Utility (`self.current_user = ...`):** Just like a Spring `@Service` singleton, a ZCA Utility is **shared across all threads/requests**! Never store per-request mutable state on `self` in a Utility.
3. **Forgetting `self` in `Interface` method signatures:** In `zope.interface.Interface`, you **omit `self`** (`def to_dict():`), whereas in the implementing class you include `self` (`def to_dict(self):`).
4. **Slow work inside a `<subscriber>`:** Zope event subscribers run **synchronously** inside the HTTP request transaction. Keep subscribers fast (or push heavy jobs like sending emails to a background queue).

---

## 5. Japan-Project Tips

- **Interface-driven testing & mocking:** Because views look up `getUtility(IEmployeeService)`, you can swap a real MySQL service with a mock utility in unit tests (`provideUtility(MockEmployeeService(), IEmployeeService)`) — just like `@MockBean` in Spring Boot!
- **Audit trail via Subscribers:** Japan enterprise projects almost always require operation audit logs (`操作ログ`). Using ZCA `<subscriber>` handlers keeps audit logging out of your core business methods.
- **Legacy Zope 2 note:** Very old Zope 2 code (pre-2006) didn't use ZCA and put logic directly on `Folder` / `SimpleItem` classes. Modern Zope 5 (and Plone) uses ZCA everywhere.

---

## 6. Example Files & How to Run

### Files in `phase-3/`
- [run.bat](./run.bat) — one-click Windows launcher
- [pyproject.toml](./pyproject.toml) — package config (`Zope[wsgi]>=5.13,<6.0`)
- [src/employee_api/interfaces.py](./src/employee_api/interfaces.py) — `IEmployee`, `IEmployeeService`, `IEmployeeSerializer`, `IAuditLogUtility`, `IEmployeeCreatedEvent`, `IEmployeeDeletedEvent`
- [src/employee_api/models.py](./src/employee_api/models.py) — `Employee` (`@implementer(IEmployee)`) + `EmployeeFolder`
- [src/employee_api/adapters.py](./src/employee_api/adapters.py) — `EmployeeJsonSerializer` (`IEmployee` -> JSON dict)
- [src/employee_api/services.py](./src/employee_api/services.py) — `EmployeeService` + `AuditLogUtility` singletons
- [src/employee_api/events.py](./src/employee_api/events.py) — `EmployeeCreatedEvent`, `EmployeeDeletedEvent`
- [src/employee_api/subscribers.py](./src/employee_api/subscribers.py) — `on_employee_created`, `on_employee_deleted`
- [src/employee_api/views.py](./src/employee_api/views.py) — thin REST views (`/api-health`, `/api-employees`, `/api-audit-logs`)
- [src/employee_api/configure.zcml](./src/employee_api/configure.zcml) — wires Utilities, Adapters, Subscribers, and Browser Views
- [api.http](./api.http) — 8 clickable test requests (including verifying audit logs captured by ZCA subscribers!)

### Quick Start (Windows)
```powershell
cd phase-3
.\run.bat
```

Then open [api.http](./api.http) and click **Send Request** on requests 1 → 8!
