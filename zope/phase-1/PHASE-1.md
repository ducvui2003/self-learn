# Phase 1 — Zope 5 Foundations & First REST API

Goal: set up a Zope 5 WSGI environment, understand how Zope handles HTTP requests (**Object Publishing & Traversal**), and run your first JSON REST API.

---

## 1. Setup & Runtime (Java Spring vs Zope 5)

In Spring Boot, Maven/Gradle downloads dependencies and starts an embedded Tomcat server.
In Zope 5, Python `venv` + `pip` (with an official Zope `constraints.txt` file) installs Zope and runs it inside a WSGI server (`waitress`).

| Concept | Java Spring Boot | Zope 5 (Python) |
| :--- | :--- | :--- |
| Runtime | JVM (Java 17/21) | Python 3.10–3.13 *(Python 3.14 uses Zope 6)* |
| Dependency manager | Maven (`pom.xml`) / Gradle | `pip` + `venv` + Zope `constraints.txt` |
| App server | Embedded Tomcat / Netty | WSGI server (`waitress` or `gunicorn`) |
| Start command | `mvn spring-boot:run` | `runwsgi etc/zope.ini` |
| Server config | `application.yml` (`server.port`) | `etc/zope.ini` (WSGI) + `etc/zope.conf` (Zope/ZODB) |
| Component scan | `@SpringBootApplication` / `@ComponentScan` | `etc/site.zcml` -> `<include package="employee_api" />` |

### Why `constraints.txt`?
Zope is built from ~80 small packages (`ZODB`, `zope.interface`, `zope.component`, `AccessControl`, etc.). Installing with `-c https://zopefoundation.github.io/Zope/releases/5.13/constraints.txt` pins every package to a tested version — just like a **Spring Boot Starter BOM** (`spring-boot-dependencies`).

---

## 2. Project & Instance Structure

A Zope app separates **instance config** (`etc/`, `var/`) from your **Python code** (`src/`):

| Path | Spring Equivalent | Purpose |
| :--- | :--- | :--- |
| `pyproject.toml` | `pom.xml` / `build.gradle` | Defines your Python package (`employee-api`) |
| `etc/zope.ini` | `application.yml` (Tomcat + logging) | WSGI server config (`waitress` on `127.0.0.1:8080`) |
| `etc/zope.conf` | `application.yml` (datasource + debug) | Zope settings and ZODB `Data.fs` file path |
| `etc/site.zcml` | `Application.java` (`@ComponentScan`) | Tells Zope which packages to load on startup |
| `var/Data.fs` | Local H2 / embedded DB file | ZODB database file (created automatically on first start) |
| `src/employee_api/configure.zcml` | `@Configuration` / `@RequestMapping` | Registers your REST views on Zope objects |
| `src/employee_api/views.py` | `@RestController` | Python classes handling HTTP requests & returning JSON |

> **Tip:** In real setups you can also generate `etc/` and `var/` using Zope's CLI tool `mkwsgiinstance -d .`, which asks for an admin username/password for the ZMI. In this phase, we already created clean `etc/` files for you.

---

## 3. Object Publishing & Traversal (The Big Mental Shift)

In **Spring MVC**, the framework matches a URL string against regex patterns:
```java
@GetMapping("/api-employees/{empCode}")
public ResponseEntity<?> getEmployee(@PathVariable String empCode) { ... }
```

In **Zope**, there is **no global route table**. Instead, Zope uses **Traversal**:
1. Zope starts at the **root object** (`/`, which implements `IApplication`).
2. It reads the first URL segment (`api-employees`) and looks up either:
   - a child object stored inside the root in ZODB, **or**
   - a **BrowserView** registered for `IApplication` with `name="api-employees"` in `configure.zcml`.
3. For any extra segment (like `EMP-0001` in `/api-employees/EMP-0001`), Zope calls `publishTraverse(request, "EMP-0001")` on that view.
4. Finally, Zope calls `__call__()` on the resolved view and sends the returned string as the HTTP response.

| Concept | Java Spring MVC | Zope 5 |
| :--- | :--- | :--- |
| Route registration | `@GetMapping("/api-employees")` | `<browser:page name="api-employees" for="OFS.interfaces.IApplication" ... />` |
| Path variable | `@PathVariable String empCode` | `IPublishTraverse` -> `publishTraverse(self, request, name)` |
| Query parameter | `@RequestParam String dept` | `self.request.form.get("dept")` |
| Request / Response | `HttpServletRequest` / `ResponseEntity` | `self.request` / `self.request.response` |
| Target domain object | Loaded manually from repository | `self.context` (already found by traversal) |

---

## 4. ZMI (Zope Management Interface)

Zope comes with a built-in web admin UI at `http://127.0.0.1:8080/manage` (roughly like Spring Boot Actuator + a live tree explorer of ZODB).

In ZMI you can:
- Browse the object tree (`/` root, folders, users in `acl_users`).
- Check the **Undo** tab (ZODB keeps transaction history).
- Inspect `error_log` for tracebacks.

To log into `/manage`, create a local admin user once with `addzopeuser` (or `mkwsgiinstance`), then open `/manage` in your browser.

---

## 5. Short Concept Note: Template Engines (Not Implemented Here)

In Spring, `@Controller` renders HTML with **Thymeleaf** (`th:text`, `th:each`, `th:if`).
In Zope, the equivalent is **ZPT (Zope Page Templates)** powered by **Chameleon**:
- Uses valid HTML with `tal:` attributes (`tal:content`, `tal:repeat`, `tal:condition`).
- Legacy Zope 2 also used **DTML** (`<dtml-var ...>`), which looks like old JSP tags.

Because our focus is **REST / JSON APIs** (like `@RestController`), we will **not** implement ZPT or DTML templates in our examples.

---

## 6. Common Pitfalls

1. **Forgetting `Content-Type: application/json; charset=utf-8`:** If you return a JSON string without setting this header, Zope may serve it as `text/html` or `text/plain`, and Japanese characters can look garbled.
2. **Forgetting `ensure_ascii=False` in `json.dumps(...)`:** Python escapes Japanese text as `\u55b6\u696d\u90e8` by default. Pass `ensure_ascii=False` to output readable UTF-8 (`営業部`).
3. **Forgetting `<include package="employee_api" />` in `etc/site.zcml`:** Your `configure.zcml` will not be loaded, and requests will return `404 Not Found`.
4. **Python version mismatch:** Zope 5 officially supports **Python 3.10–3.13**. If your machine only has **Python 3.14**, install **Zope 6** (`constraints.txt` for `6.x`) or install Python 3.12/3.13.
5. **Missing `var/` directory:** Zope needs the `var/` folder to exist before creating `var/Data.fs`. Create it (`mkdir var`) before the first `runwsgi`.

---

## 7. Japan-Project Tips

- **Always use a consistent JSON envelope:** Wrap responses in `{"status": "ok", "data": ..., "timestamp": "..."}` and errors in `{"status": "error", "error": {"code": "E_NOT_FOUND", "message": "..."}}`. Japan enterprise API specs almost always require fixed status + business error codes.
- **Explicit JST timezone (`+09:00`):** Use ISO-8601 timestamps with explicit offset (`2020-04-01T09:00:00+09:00`) so frontend and MySQL clients never guess local time.
- **Legacy Zope 2 note:** In old Zope 2 projects, you may see endpoints written directly inside ZMI as "Script (Python)" objects instead of `BrowserView` classes in `src/`. Modern Zope 5 keeps all API code in Git-tracked Python packages like this phase.

---

## 8. Example Files & How to Run

### Files in `phase-1/`
- [run.bat](./run.bat) — **one-click Windows launcher** (creates shared `..\.venv` if missing, installs Zope 5 + package, starts server)
- [pyproject.toml](./pyproject.toml) — package definition (`employee-api`)
- [src/employee_api/configure.zcml](./src/employee_api/configure.zcml) — registers `/api-health` and `/api-employees`
- [src/employee_api/views.py](./src/employee_api/views.py) — `BaseJsonView`, `HealthApiView`, `EmployeesApiView` (with `IPublishTraverse`)
- [src/employee_api/data.py](./src/employee_api/data.py) — Japan-enterprise sample employee data (JP/EN)
- [etc/zope.ini](./etc/zope.ini) — WSGI server config (`waitress` on port `8080`)
- [etc/zope.conf](./etc/zope.conf) — Zope instance + ZODB `Data.fs` config
- [etc/site.zcml](./etc/site.zcml) — loads `Products.Five` and `employee_api`
- [api.http](./api.http) — one-click HTTP test file (VS Code REST Client / IntelliJ HTTP Client)

### Quick Start (Windows — `run.bat`)
Just run [run.bat](./run.bat) (double-click it, or run from PowerShell inside `phase-1/`):

```powershell
cd phase-1
.\run.bat
```

### Standard Cross-Platform Setup (macOS / Linux / CI / without `run.bat`)
All dependencies (including `Zope[wsgi]>=5.13,<6.0`) are declared directly in [pyproject.toml](./pyproject.toml):

```bash
# From zope/ folder (Python 3.10-3.13)
python3 -m venv .venv
.venv/bin/python -m pip install -e ./phase-1

# Start Zope 5
cd phase-1
mkdir -p var
../.venv/bin/runwsgi -v etc/zope.ini
```

### Optional: Create a ZMI Admin User (`/manage`)
```powershell
cd phase-1
..\.venv\Scripts\addzopeuser -c etc/zope.conf admin admin
```

### Step 3: Test the API
- **Click-to-run (like Postman):** Open [api.http](./api.http) in VS Code (with the **REST Client** extension) or IntelliJ and click **Send Request**.
- **Or use `curl`:**
```powershell
curl http://127.0.0.1:8080/api-health
curl http://127.0.0.1:8080/api-employees
curl "http://127.0.0.1:8080/api-employees?dept=Engineering"
curl http://127.0.0.1:8080/api-employees/EMP-0001
curl http://127.0.0.1:8080/api-employees/EMP-9999
```
