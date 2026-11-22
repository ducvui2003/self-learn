# AGENT.md — Context & Conventions for Zope (Python) Learning Project

> Read this file first. It lets any agent or chat continue the work consistently.

## 1. Goal
- Topic: **Modern Zope (Zope 5 on Python 3, WSGI)** focused on building **REST / JSON APIs** (like Spring `@RestController`).
- The user is a **backend developer who knows Java Spring** (Spring Boot, Spring MVC, Spring DI, Spring Security, Spring Data JPA) and will use **MySQL** with Zope for a **Japan client project**. Map each Zope concept to its Java Spring equivalent (use comparison tables).
- **No HTML template implementation in examples:** Mention Zope template engines (ZPT/Chameleon, DTML) only in short concept notes (for awareness, like `@Controller` + Thymeleaf in Spring). All runnable examples should expose **JSON / REST API endpoints**.
- Keep explanations concise and practical for real enterprise codebases.
- Also show legacy Zope 2 style (Through-The-Web scripts, DTML, ZSQL Methods + `ZMySQLDA`, `zc.buildout`) in one short note where relevant, because many real Zope projects are long-running legacy systems.

## 2. Folder structure (`zope/`)
| Path | Purpose |
| :--- | :--- |
| `ROADMAP.md` | Master roadmap: Java Spring vs Zope mental-model table + 6 phases. Mark finished phases with ✅ Ready. |
| `phase-N/` | **One folder per phase**. Contains the guide and a runnable REST API example. |
| `phase-N/PHASE-N.md` | Study guide for that phase (concepts + Java Spring / Zope mapping tables). |
| `phase-N/` | Runnable Zope 5 REST API example (clean package under `src/employee_api/`, instance config, `run.bat` one-click setup/start, and `api.http` for HTTP testing). |

## 3. Rules for creating a new phase
1. The user says which phase to do next (for example "start phase 1"). Do only that phase.
2. Create `phase-N/` with `PHASE-N.md` and a runnable REST API example.
3. `PHASE-N.md` must include:
   - a Java Spring / Zope mapping table for each topic;
   - the common pitfalls (for example ZODB mutability `_p_changed`, Acquisition surprises, missing ZCML, setting `Content-Type: application/json`);
   - Japan-project tips (enterprise style + legacy Zope 2 notes);
   - a section pointing to the example files, `api.http`, and sample `curl` requests.
4. The example must be a small, realistic Japan-enterprise REST API (for example an Employee Directory & HR JSON API with JP/EN data like `営業部 (Sales)` and `EMP-0001`). Comment each concept where it is used. Do **not** build HTML/ZPT views in examples.
   - Always include an `api.http` file in `phase-N/` (VS Code REST Client / IntelliJ HTTP Client format, using `@baseUrl` variables and `###` separators) covering all endpoints (happy paths + error cases) so the user can click to run and test like Postman.
5. **Shared Python virtual environment & clean package naming:** keep ONE `.venv` at `zope/.venv`. Define all dependencies (including `"Zope[wsgi]>=5.13,<6.0"` and any phase-specific libs) directly inside each phase's **`pyproject.toml`** (do not use `requirements.txt`), so any developer on Windows/Mac/Linux/CI can install with `python -m pip install -e .`.
   - **Clean `src/` naming:** Name the Python package inside `src/` cleanly by domain (for example `src/employee_api/`), **not** `phase1_api` or `phase2_api`.
   - Each `phase-N/` holds its own Zope package (`pyproject.toml`, `src/employee_api/` with `configure.zcml` and Python modules), instance config (`etc/zope.ini`, `etc/zope.conf`, `etc/site.zcml`), `api.http`, and a Windows **`run.bat`** script.
   - **`run.bat` rule:** Every `phase-N/run.bat` is a convenience wrapper that checks `..\.venv`, creates it if missing (using Python 3.12/3.13), runs `"%VENV_PY%" -m pip install -e .`, ensures `var/` exists, and starts `runwsgi -v etc\zope.ini`. Always use CRLF line endings and `"%VENV_PY%" -m pip`.
   - Do not commit `var/` (ZODB `Data.fs`, logs) or `.venv/` files into git.
6. After finishing, update `ROADMAP.md` (link the phase, mark it ✅ Ready) and the status table below, then summarize with clickable file links.

## 4. Japan-client implementation style
Keep these patterns in mind for guides and examples:
- **Standardized JSON response format:** Return a consistent wrapper (`{"status": "ok", "data": ...}` or `{"status": "error", "error": {"code": "E_NOT_FOUND", "message": "..."}}`) with explicit business error codes, not bare strings.
- **Strict layered architecture:** Separate REST View (Controller) → Service (ZCA Utility / business logic) → Repository/DAO (MySQL or ZODB) → Schema/DTO.
- **MySQL table conventions:** Use `utf8mb4`, soft delete (`deleted_flg`), audit columns (`created_at`, `created_by`, `updated_at`, `updated_by`), and optimistic locking (`version` or `updated_at` check) where appropriate.
- **Date/time & encoding:** Use UTF-8 everywhere (note legacy Shift-JIS / CP932 pitfalls for CSV exports) and explicit timezone handling (JST `+09:00` or UTC ISO-8601).
- **Strict input validation & logging:** Validate required fields, max length, code formats (e.g., `EMP-0001`), and log request/error context cleanly for incident checks.
- **Legacy Zope 2 coexistence:** Many Japan enterprise systems run long-lived Zope 2 code (ZMI TTW scripts, `ZSQLMethods`, `ZMySQLDA`) while gradually adding modern Zope 5 REST APIs for a new frontend (e.g., Angular).

## 5. Roadmap status
| Phase | Topic | Status |
| :--- | :--- | :--- |
| 1 | Setup, Zope 5 WSGI instance, ZMI, object publishing & traversal, first JSON API endpoint | ✅ Done (`phase-1/`) |
| 2 | ZODB (object database), `Persistent`, `BTrees`, ACID transactions, Acquisition | ✅ Done (`phase-2/`) |
| 3 | ZCA (`zope.interface`, `zope.component`), ZCML, Browser Views as REST handlers, Utilities, Adapters, Events | ✅ Done (`phase-3/`) |
| 4 | REST API Deep Dive: HTTP verbs, JSON body parsing, validation, error handling, status codes, CORS, pagination | ✅ Done (`phase-4/`) |
| 5 | Security (Users, Roles, Local Roles, Permissions, API Auth), MySQL integration (`SQLAlchemy` + `zope.sqlalchemy` & legacy `ZSQLMethods`) | ✅ Done (`phase-5/`) |
| 6 | Testing (API tests), `ZCatalog` search, performance & clustering (ZEO/RelStorage), deployment, legacy Zope 2 | ✅ Done (`phase-6/`) |

## 6. Language rules
- **Main language: English.** Write all guides, code comments and replies in English.
- **Use basic words.** Use short sentences and simple words. Avoid hard or rare words. If a technical term is needed, explain it in one simple line.
- Japanese text may appear only inside example data (for example department names like `営業部` in JSON payloads), always with an English meaning next to it.

## 7. Communication preferences
- The user writes informal English, so reply simply and concisely.
- Use markdown with clickable file links.
- Ask before changing the roadmap structure.
