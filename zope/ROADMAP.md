# Zope (Python) Roadmap — REST API Track

Goal: learn **Zope 5 (Python)** to build **REST / JSON APIs** from a **Java Spring** backend developer background, using **MySQL** for relational data. Each Zope concept is mapped to what you already know in Spring Boot / Spring MVC / Spring Security / Spring Data.

> **Note on HTML Templates:** Zope has built-in template engines (ZPT/Chameleon, legacy DTML — similar to `@Controller` + Thymeleaf in Spring). This roadmap explains them briefly for awareness, but all runnable examples focus purely on **REST / JSON APIs** (like `@RestController`).

## Mental-model mapping (Java Spring vs Zope)

| Concept | Java Spring (Boot) | Zope 5 (Python) |
| :--- | :--- | :--- |
| App server / runtime | Embedded Tomcat / Netty (JVM) | WSGI server (`waitress` / `gunicorn`, Python 3) |
| Request routing | URL pattern matching (`@GetMapping("/users/{id}")`) | **Object Traversal** — URL walks a tree of real objects (`/api/users/u1`) |
| REST Controller | `@RestController` | **BrowserView** (`Products.Five.browser.BrowserView`) returning JSON + status codes |
| DI / IoC container | Spring ApplicationContext (`@Bean`, `@Autowired`) | **ZCA** (`zope.component`: Utilities, Adapters, Subscribers) |
| Interfaces / contracts | Java `interface` + `implements` | `zope.interface.Interface` + `@implementer(...)` |
| Service singleton | `@Service` / `@Component` | **Utility** (`<utility>` in ZCML) |
| Strategy / Converter | `Converter<S, T>` / Strategy bean | **Adapter** (`<adapter>` adapts object A to interface B) |
| Configuration | `@Configuration` / `application.yml` / XML | `configure.zcml` (component wiring) + `zope.conf` & `zope.ini` (server/DB) |
| Database / Persistence | MySQL + JPA / Hibernate / Spring Data | **ZODB** (internal app tree) + **MySQL** via `SQLAlchemy` + `zope.sqlalchemy` (legacy: `ZSQLMethods` + `ZMySQLDA`) |
| Transactions | `@Transactional` (per-method / filter) | Automatic **per-HTTP-request** ACID transaction (`transaction` package, syncs ZODB + MySQL) |
| HTML Templates *(concept only)* | `@Controller` + Thymeleaf | **ZPT / Chameleon** (`tal:content`, `tal:repeat`) — not used in REST API examples |
| Security / RBAC | Spring Security (`@PreAuthorize`, `GrantedAuthority`) | Built-in **Object-level RBAC** (`AccessControl`: Users, Roles, Local Roles, Permissions) |
| Domain events | `ApplicationEventPublisher` + `@EventListener` | `zope.event` + `<subscriber>` (ObjectAdded, ObjectModified, custom events) |
| Admin / Inspection UI | Actuator / custom admin dashboard | **ZMI** (Zope Management Interface at `/manage`) built in |
| Context inheritance | No direct equivalent (closest: bean scopes) | **Acquisition** — child objects inherit methods/attributes/security from parent folders |
| Build & deps | Maven / Gradle (`pom.xml`, `build.gradle`) | `pip` + `venv` + Zope constraints file (legacy: `zc.buildout`) |

## Phases

| Phase | Topic | Status |
| :--- | :--- | :--- |
| 1 | Setup, Zope 5 WSGI instance, ZMI, object publishing & traversal, first JSON API endpoint | ✅ Ready — [phase-1/PHASE-1.md](./phase-1/PHASE-1.md) |
| 2 | ZODB (object database), `Persistent`, `BTrees`, ACID transactions, Acquisition | ✅ Ready — [phase-2/PHASE-2.md](./phase-2/PHASE-2.md) |
| 3 | ZCA (`zope.interface`, `zope.component`), ZCML, Browser Views as REST handlers, Utilities, Adapters, Events | ✅ Ready — [phase-3/PHASE-3.md](./phase-3/PHASE-3.md) |
| 4 | REST API Deep Dive: HTTP verbs, JSON body parsing, validation, error handling, status codes, CORS, pagination | ✅ Ready — [phase-4/PHASE-4.md](./phase-4/PHASE-4.md) |
| 5 | Security (Users, Roles, Local Roles, Permissions, API Auth), MySQL integration (`SQLAlchemy` + `zope.sqlalchemy` & legacy `ZSQLMethods`) | ✅ Ready — [phase-5/PHASE-5.md](./phase-5/PHASE-5.md) |
| 6 | Testing (API tests), `ZCatalog` search, performance & clustering (ZEO/RelStorage), deployment, legacy Zope 2 | ✅ Ready — [phase-6/PHASE-6.md](./phase-6/PHASE-6.md) |

### Phase 1 — Foundations & Setup
- Install Python 3, create shared `.venv`, install Zope 5 with official constraints
- Create and run a WSGI instance (`mkwsgiinstance`, `runwsgi`, `zope.ini`, `zope.conf`)
- Explore the ZMI (`/manage`): object tree, folders, Undo tab, error log
- Core mental shift: **Object Publishing & Traversal** vs Spring MVC `@RequestMapping`
- Short concept note on ZPT / Chameleon templates (no template code)
- Example: minimal Employee JSON API (`GET /api/health`, `GET /api/employees`)

### Phase 2 — ZODB, Persistence & Acquisition
- How **ZODB** works: storing Python object graphs directly in `Data.fs` (and why Zope still uses it even when business data is in MySQL)
- `Persistent` base class, `OFS.Folder`, `OFS.SimpleItem`, and `BTrees` (`OOBTree`, `IOBTree`)
- Pitfall: mutating lists/dicts (`_p_changed = True` or `PersistentList` / `PersistentMapping`)
- Automatic ACID transactions per request (`transaction.commit()`, `abort()`, `ConflictError` retries) vs Spring `@Transactional`
- **Acquisition**: how child objects look up attributes/methods from parents (and when to avoid it)
- Example: JSON API reading/writing persistent `EmployeeFolder` and `Employee` objects in ZODB

### Phase 3 — ZCA (Zope Component Architecture) & REST Views
- `zope.interface`: defining contracts with `Interface` and `@implementer`
- `zope.component`: registering and looking up **Utilities** (like Spring `@Service`) and **Adapters** (like DTO serializers/converters)
- Wiring components with `configure.zcml` (like Spring XML / `@Configuration`)
- **Browser Views** (`BrowserView` + `<browser:page>`): using views as REST handlers (like Spring `@RestController`)
- Events & Subscribers (`zope.event`, `IObjectAddedEvent`, custom events) vs Spring `ApplicationEvent`
- Example: refactor Employee JSON API into clean Interfaces, Service Utilities, Serializer Adapters, and REST Views

### Phase 4 — REST API Deep Dive
- Handling HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) in Zope (`self.request.method` + custom traversal / REST base view)
- Reading JSON request bodies (`self.request.get('BODY')`), query params, path segments, headers
- Validation & serialization (`zope.schema` or Pydantic/dataclasses) vs Spring `@Valid` + Jackson
- Consistent JSON error handling (`@ControllerAdvice` equivalent in Zope: exception views `<browser:page for="Exception">`), HTTP status codes, CORS headers
- Search, filtering, and pagination (`?page=1&size=20&q=...`)
- Short concept note on ZPT/TAL/METAL (awareness only, not implemented)
- Example: Full Employee CRUD REST API with validation, pagination, and global JSON error handler

### Phase 5 — Security & MySQL Integration
- Zope Security model: Users (`acl_users`), Roles, **Local Roles** (per-folder roles), and Permissions vs Spring Security
- Declarative protection: `ClassSecurityInfo`, `declareProtected`, and ZCML `permission="..."` vs `@PreAuthorize`
- API authentication patterns in Zope (HTTP Basic Auth, custom Bearer/JWT auth with PAS / PluggableAuthService)
- **Modern MySQL in Zope 5:** `SQLAlchemy` + `PyMySQL`/`mysqlclient` + `zope.sqlalchemy` (connection pooling + two-phase transaction sync with ZODB) vs Spring Data JPA + HikariCP
- **Legacy MySQL in Zope:** `Products.ZMySQLDA` + `Products.ZSQLMethods` (`<dtml-sqlvar>`, `<dtml-sqltest>`) — similar to MyBatis XML mappers
- Example: Role-protected Employee REST API backed by MySQL (`employees` + `audit_logs` tables)

### Phase 6 — Testing, Performance, Deployment & Legacy Zope
- Testing REST APIs: `pytest` / `zope.testrunner`, `ZopeTestCase`, WSGI test client (`WebTest`) vs JUnit + `MockMvc`
- Indexing & searching ZODB objects with **ZCatalog**
- Scaling & performance: ZEO / RelStorage (storing ZODB in MySQL for multi-worker setups), connection pooling, packing `Data.fs`
- Production deployment: WSGI (`waitress` / `gunicorn`) behind Nginx, structured logging, health checks
- Legacy Zope 2 guide: TTW Python Scripts, DTML, ZSQL Methods, `zc.buildout`, `Products.*`, and how **Plone** / `plone.restapi` builds on Zope
