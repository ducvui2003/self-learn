# Phase 4 — REST API Deep Dive

Goal: build a production-grade Zope 5 REST API with an **HTTP-verb dispatcher** (`GET.py`, `POST.py`, `PUT.py`, `PATCH.py`, `DELETE.py`), **strict field validation**, **optimistic locking (`version`)**, **global JSON error handling**, **CORS**, and **search/sort/pagination**.

---

## 1. REST Architecture (Java Spring vs Zope 5)

| REST Feature | Java Spring Boot | Zope 5 (Phase 4 Pattern) |
| :--- | :--- | :--- |
| HTTP verb routing | `@GetMapping`, `@PostMapping`, `@PutMapping`, `@PatchMapping`, `@DeleteMapping` | `RestDispatcherView` reads `self.request.method` and routes to `GET.py`, `POST.py`, `PUT.py`, `PATCH.py`, `DELETE.py` |
| JSON request body | `@RequestBody EmployeeRequest` | `self.request.get("BODY")` -> `json.loads(...)` |
| Input validation | `@Valid` + `@NotBlank` / `@Pattern` / `@Email` | `schemas.py` returning field-level error list (`details: [{field, message}]`) |
| Optimistic locking | JPA `@Version` (`OptimisticLockException` -> `409`) | `emp.version` checked on `PUT`/`PATCH` -> `409 E_VERSION_CONFLICT` |
| Global error handler | `@RestControllerAdvice` + `@ExceptionHandler` | `try/except` boundary in `RestDispatcherView` (or Zope Exception Views `<browser:page for="Exception">`) |
| CORS | `@CrossOrigin` / `WebMvcConfigurer` | `Access-Control-Allow-*` headers + `OPTIONS` returning `204 No Content` |
| Pagination | `Pageable` + `Page<EmployeeDto>` | `?page=1&size=10&sort=empCode&order=asc` -> `pagination: {page, size, totalCount, totalPages}` |

---

## 2. Why `GET.py`, `POST.py`, `PUT.py`, `PATCH.py`, `DELETE.py`?

In many real Zope enterprise codebases, putting all 5 HTTP methods into one giant `views.py` makes files hard to read and causes Git merge conflicts.

Instead, we build ONE reusable **`RestDispatcherView`** ([rest/dispatcher.py](./src/employee_api/rest/dispatcher.py)) that handles:
1. Traversal (`IPublishTraverse` -> `self.subpath`)
2. CORS headers & `OPTIONS` preflight (`204 No Content`)
3. Global error handling (catches `ApiError` and unexpected `Exception`, calls `transaction.abort()` on `500`, and **always returns JSON — never Zope's HTML traceback page**)
4. Dispatching `self.request.method` to small, single-responsibility files:
   - `rest/employees/GET.py`
   - `rest/employees/POST.py`
   - `rest/employees/PUT.py`
   - `rest/employees/PATCH.py`
   - `rest/employees/DELETE.py`

---

## 3. Short Concept Note: Zope Template Engines (Awareness Only)

*(Not implemented in our REST examples, per project conventions.)*

If you encounter HTML pages in an existing Zope codebase:
- **ZPT / Chameleon** (modern, like **Thymeleaf**): valid HTML files (`.pt`) with `tal:content`, `tal:repeat`, `tal:condition`, `tal:attributes`, and reusable page layouts via **METAL** (`metal:define-macro` / `metal:use-macro`).
- **DTML** (legacy Zope 2, like old **JSP**): `<dtml-var name>`, `<dtml-in items>`.

---

## 4. Common Pitfalls

1. **WebDAV hijacking `PUT`, `PATCH`, `DELETE`, `OPTIONS`:** Without the `@@` prefix (`/@@api-employees/...`), Zope's `OFS.Folder` intercepts `PUT`/`DELETE` as WebDAV requests and returns `404` (`webdav.NullResource`). Always use `/@@...` for REST `BrowserView`s, or use `plone.rest` / a custom traverser.
2. **Returning Zope's HTML error page on `500`:** If an unhandled exception escapes your view, Zope returns an HTML error page instead of JSON, breaking frontend clients (Angular/React). Always wrap REST dispatch in a global `try/except Exception` (plus `transaction.abort()`).
3. **Forgetting `OPTIONS` for CORS:** Browsers (like an Angular frontend on `localhost:4200`) send an `OPTIONS` preflight request before `POST`/`PUT`/`DELETE` with `Content-Type: application/json`. If your dispatcher doesn't return `204` + `Access-Control-Allow-*` headers, the browser blocks the API call.
4. **In-memory `self.request.get("BODY")` vs `self.request.form`:**
   - Query params (`?page=1&dept=Sales`) and HTML form fields live in `self.request.form`.
   - Raw JSON bodies (`application/json`) live in `self.request.get("BODY")`.

---

## 5. Japan-Project Tips

- **Optimistic locking (`version`):** Japan enterprise specs almost always require conflict detection when two users edit the same screen at the same time (`排他制御`). Sending `version` in `PUT` and returning `409 E_VERSION_CONFLICT` if stale is standard practice.
- **Field-level validation errors:** Return `error.details = [{"field": "...", "message": "..."}]` so the Angular/frontend form can highlight every invalid input at once.
- **Auto-fill Japanese department labels:** Notice `schemas.py` maps `"Engineering"` -> `"開発部"` automatically when `departmentJa` is omitted.

---

## 6. Example Files & How to Run

### Files in `phase-4/`
- [run.bat](./run.bat) — one-click Windows launcher
- [pyproject.toml](./pyproject.toml) — defines `Zope[wsgi]>=5.13,<6.0`
- [src/employee_api/rest/dispatcher.py](./src/employee_api/rest/dispatcher.py) — `RestDispatcherView` (CORS, `OPTIONS`, verb dispatch, global JSON error boundary)
- [src/employee_api/rest/employees/GET.py](./src/employee_api/rest/employees/GET.py) — search (`?q=`), filter (`?dept=`), sort, paginate, single get, `?crash=true` 500 demo
- [src/employee_api/rest/employees/POST.py](./src/employee_api/rest/employees/POST.py) — create with strict validation
- [src/employee_api/rest/employees/PUT.py](./src/employee_api/rest/employees/PUT.py) — full update + optimistic locking (`version`)
- [src/employee_api/rest/employees/PATCH.py](./src/employee_api/rest/employees/PATCH.py) — partial update
- [src/employee_api/rest/employees/DELETE.py](./src/employee_api/rest/employees/DELETE.py) — logical soft delete
- [src/employee_api/schemas.py](./src/employee_api/schemas.py) — field-level input validation
- [src/employee_api/exceptions.py](./src/employee_api/exceptions.py) — `ApiError`, `ValidationError`, `NotFoundError`, `ConflictError`
- [api.http](./api.http) — 11 clickable requests testing every verb, pagination, validation, version conflict, CORS `OPTIONS`, and 500 JSON handler

### Quick Start (Windows)
```powershell
cd phase-4
.\run.bat
```

Open [api.http](./api.http) and click **Send Request** on requests 1 → 11!
