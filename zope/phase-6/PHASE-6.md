# Phase 6 — Testing, Indexing, Scaling, Deployment & Legacy Zope 2

Goal: learn how to **test Zope REST APIs** (`pytest` + `WebTest`), **index ZODB objects** (`ZCatalog` / `BTrees`), **scale & deploy** Zope 5 in production, and navigate **legacy Zope 2** enterprise codebases.

---

## 1. Testing REST APIs (Java Spring vs Zope 5)

| Concept | Java Spring Boot | Zope 5 |
| :--- | :--- | :--- |
| Test runner | JUnit 5 (`mvn test`) | `pytest` (or `zope.testrunner`) |
| HTTP integration test | `@SpringBootTest` + `MockMvc` | `paste.deploy.loadapp("config:etc/zope.ini")` + `webtest.TestApp` |
| Mock a service | `@MockBean` | `zope.component.provideUtility(MockService(), IEmployeeService)` |
| Fast in-process run | No network socket needed | `WebTest` calls the WSGI app directly in Python (no port binding!) |

See [tests/test_api.py](./tests/test_api.py) — run it anytime with `.\test.bat`!

---

## 2. Indexing ZODB Objects (`ZCatalog` & `BTrees`)

In MySQL, you create `CREATE INDEX idx_dept ON employees(department_en)`.
In ZODB, scanning all objects in a folder is O(N) and loads every object from disk.

Zope solves this with **`BTrees` inverted indexes** (and the **`Products.ZCatalog`** add-on built on top of them):
- **FieldIndex** (`by_dept["engineering"] -> OOTreeSet({"EMP-0002", "EMP-0004"})`) — exact match on one field
- **KeywordIndex** (`by_skill["mysql"] -> OOTreeSet({"EMP-0002", "EMP-0004"})`) — matches items in a list
- **Set intersection** (`BTrees.OOBTree.intersection(dept_ids, skill_ids)`) — combines multiple filters in O(log N) without loading non-matching objects!

*(When your main business data is in **MySQL**, use normal MySQL indexes; use `ZCatalog` / `BTrees` when searching objects stored in ZODB.)*

---

## 3. Scaling & Performance (Multi-Worker Zope)

By default, `<filestorage>` (`var/Data.fs`) can only be opened by **one OS process** at a time.
To run multiple Zope worker processes behind a load balancer (like scaling Spring Boot pods):

| Storage Option | How it works | When to use |
| :--- | :--- | :--- |
| **FileStorage** (`Data.fs`) | Single process, local file | Local dev / small single-server apps |
| **ZEO** (Zope Enterprise Objects) | Dedicated ZODB server process; multiple Zope workers connect over TCP | Classic Zope multi-process cluster |
| **RelStorage (on MySQL!)** | Stores ZODB pickles directly inside **MySQL** tables (`object_state`, `transaction`) | Best fit when your ops team already runs HA MySQL! |

### Performance Tuning Checklist
- **`cache-size`** in `etc/zope.conf`: number of ZODB objects kept in RAM per connection (e.g. `30000`).
- **`threads`** in `etc/zope.ini`: Waitress thread count (usually `2–4` per process; scale horizontally with multiple processes via Gunicorn or multiple Waitress instances behind Nginx).
- **Pack `Data.fs` regularly:** Run weekly cron packing to remove old undo history and keep `Data.fs` compact.
- **SQLAlchemy pool:** Keep `pool_pre_ping=True` and `pool_recycle=1800` for MySQL.

---

## 4. Production Deployment (Nginx + WSGI)

Typical Linux production architecture (very similar to Spring Boot behind Nginx):

```text
Client / Angular SPA
  -> Nginx (HTTPS/TLS, gzip, static files, rate limits, load balancing)
    -> Zope 5 WSGI workers (Waitress or Gunicorn on 127.0.0.1:8081, 8082, ...)
      -> MySQL (business tables via SQLAlchemy + optional RelStorage for ZODB)
```

Key production settings in `etc/zope.conf`:
- Set **`debug-mode off`** (critical — disables slow debug checks and prevents verbose error leaks).
- Set **`verbose-security off`**.
- Log **`X-Request-Id`**, method, path, status, and **`durationMs`** on every request (see [views.py](./src/employee_api/views.py)) for fast incident investigation (`障害調査`).

---

## 5. Legacy Zope 2 Maintenance Guide (What You May See at Work)

Many long-running Japan enterprise systems were built on **Zope 2** (10–20 years ago) and are migrating gradually to Zope 5 + REST APIs:

| Legacy Zope 2 Feature | What it looks like | Modern Zope 5 Equivalent |
| :--- | :--- | :--- |
| **TTW Python Scripts** | Code stored inside ZODB/ZMI (`Products.PythonScripts`) | Git-tracked Python modules in `src/` |
| **DTML** | `<dtml-var title>`, `<dtml-in items>` | ZPT/Chameleon (HTML) or JSON `BrowserView` (REST) |
| **ZSQL Methods + `ZMySQLDA`** | SQL queries inside ZMI with `<dtml-sqlvar>` | `SQLAlchemy` + `PyMySQL` + `zope.sqlalchemy` |
| **`zc.buildout`** | `buildout.cfg` + `bin/buildout` + `bin/instance fg` | `pyproject.toml` + `venv` + `pip` + `runwsgi` |
| **`Products.*` namespace** | Packages named `Products.MyApp` | Standard `src/employee_api/` package |
| **Plone / `plone.restapi`** | Enterprise CMS built on Zope with `@employees` JSON endpoints | Same ZCA + Traversal + ZODB core you learned in Phases 1–6! |

---

## 6. Example Files & How to Run

### Files in `phase-6/`
- [run.bat](./run.bat) — starts Zope 5 server (`http://127.0.0.1:8080`)
- [test.bat](./test.bat) — **one-click `pytest` runner** (runs all 4 automated API tests!)
- [tests/test_api.py](./tests/test_api.py) — `pytest` + `WebTest` integration test suite
- [src/employee_api/catalog.py](./src/employee_api/catalog.py) — `OOBTree` + `OOTreeSet` indexed search (`FieldIndex` + `KeywordIndex` pattern)
- [src/employee_api/views.py](./src/employee_api/views.py) — `ObservableJsonView` (`X-Request-Id` + `durationMs` structured access logs)
- [api.http](./api.http) — 6 clickable requests testing health probe, indexed search, create+index, and `X-Request-Id`

### Run Automated Tests
```powershell
cd phase-6
.\test.bat
```

### Run Live Server
```powershell
cd phase-6
.\run.bat
```
