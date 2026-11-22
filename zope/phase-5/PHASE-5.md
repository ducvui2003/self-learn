# Phase 5 — Zope Security & MySQL Integration

Goal: secure your Zope REST API with **Users, Roles, and Permissions** (like Spring Security), and connect Zope cleanly to **MySQL** using **SQLAlchemy + `PyMySQL` + `zope.sqlalchemy`** (plus learn how legacy Zope 2 connects via `ZMySQLDA` + `ZSQLMethods`).

---

## 1. Zope Security vs Spring Security

| Concept | Java Spring Security | Zope 5 (`AccessControl`) |
| :--- | :--- | :--- |
| User store | `UserDetailsService` | `acl_users` folder in ZODB (or **PAS / PluggableAuthService** for LDAP / JWT / OAuth) |
| Current user | `SecurityContextHolder.getContext().getAuthentication()` | `AccessControl.getSecurityManager().getUser()` |
| Roles | `GrantedAuthority` (`ROLE_HR_MANAGER`) | Roles (`Manager`, `HRManager`, `Viewer`, `Authenticated`, `Anonymous`) |
| Folder-level roles | Custom ACL / Spring Security ACL | **Local Roles** (built-in: grant `HRManager` only on `/departments/hr`!) |
| Method / endpoint guard | `@PreAuthorize("hasRole('HR_MANAGER')")` | ZCML `permission="..."`, `ClassSecurityInfo.declareProtected(...)`, or explicit role check for JSON 401/403 |
| API auth | HTTP Basic / Bearer JWT filter | HTTP Basic (built-in) or Bearer JWT via a PAS plugin / `RestDispatcherView` |

### Important REST API Security Tip
If you put a restricted ZCML `permission="zope2.ViewManagementScreens"` directly on a `<browser:page>`, Zope returns a browser Basic Auth challenge or an **HTML `Unauthorized` page**.
For JSON REST APIs, teams often use `permission="zope2.View"` in ZCML and check `getSecurityManager().getUser()` in their base REST view so they can return clean **JSON `401 E_UNAUTHORIZED` / `403 E_FORBIDDEN`** envelopes!

---

## 2. Modern MySQL in Zope 5 (`SQLAlchemy` + `PyMySQL` + `zope.sqlalchemy`)

| Concept | Java Spring Boot + MySQL | Zope 5 + MySQL |
| :--- | :--- | :--- |
| ORM / Entity | JPA / Hibernate (`@Entity`) | `SQLAlchemy 2.x` (`DeclarativeBase`) |
| JDBC Driver | `mysql-connector-j` | `PyMySQL` (pure Python, easy on Windows) or `mysqlclient` (C driver) |
| Connection Pool | HikariCP | SQLAlchemy `create_engine(..., pool_size=5, pool_pre_ping=True, pool_recycle=1800)` |
| Transactions | `@Transactional` | `zope.sqlalchemy.register(DBSession)` — joins Zope's per-request `transaction`! |
| Commit / Rollback | Spring TransactionManager | **Automatic two-phase commit** across ZODB + MySQL! Never call `session.commit()` manually. |

### Connecting to Real MySQL vs Local SQLite Fallback
In [db.py](./src/employee_api/db.py):
- By default (`DATABASE_URL` unset), it uses local SQLite (`var/employees.db`) so `.\run.bat` works immediately with zero setup.
- To connect to your **MySQL** server (e.g., Laragon MySQL or Docker MySQL):
  1. Run [mysql_schema.sql](./mysql_schema.sql) in MySQL.
  2. Set `DATABASE_URL` before running `.\run.bat`:
     ```powershell
     $env:DATABASE_URL = "mysql+pymysql://root:your_password@127.0.0.1:3306/zope_hr?charset=utf8mb4"
     .\run.bat
     ```

---

## 3. Legacy MySQL in Zope 2 (`Products.ZMySQLDA` + `Products.ZSQLMethods`)

In older Japan enterprise Zope 2 / Zope 5 systems, you will frequently see **ZSQL Methods** instead of SQLAlchemy (very similar to **MyBatis XML mappers**):

1. A **`ZMySQLDA`** database connection object lives inside ZMI (e.g., `/mysql_conn`).
2. SQL queries are saved as **`ZSQL Method`** objects using DTML SQL tags:
   ```sql
   SELECT emp_code, name_en, name_ja
   FROM employees
   WHERE deleted_flg = 0
     AND department_en = <dtml-sqlvar dept type="string">
   ```
   - `<dtml-sqlvar ... type="string|int|float">` automatically escapes values to prevent SQL injection (like MyBatis `#{dept}`).
   - `<dtml-sqltest ... op="eq">` builds `col = 'val'` safely.
3. Python code calls it directly by Acquisition: `rows = context.get_employees_by_dept(dept="Engineering")`.

---

## 4. Common Pitfalls

1. **Calling `session.commit()` manually with `zope.sqlalchemy`:** Do **NOT** call `session.commit()` — `zope.sqlalchemy` raises an error or breaks two-phase commit. Use `session.flush()` if you need an auto-increment `id`, and let Zope commit automatically at request end!
2. **MySQL 8-hour idle timeout (`MySQL server has gone away`):** Always set `pool_pre_ping=True` and `pool_recycle=1800` in `create_engine(...)`.
3. **Forgetting `?charset=utf8mb4` in `DATABASE_URL`:** Old MySQL `utf8` (3-byte) corrupts rare Japanese Kanji (surrogate pairs) and emoji. Always use `utf8mb4` on both the table DDL and connection string.
4. **Hardcoding DB credentials in `zope.conf` or Python files:** Always pass `DATABASE_URL` via environment variables or secret config files outside Git.

---

## 5. Japan-Project Tips

- **Standard MySQL columns:** Notice [mysql_schema.sql](./mysql_schema.sql) includes `deleted_flg`, `version`, `created_at`, `created_by`, `updated_at`, `updated_by` — the standard audit columns expected in Japan enterprise DB reviews (`テーブル定義書`).
- **Actor tracking (`created_by` / `updated_by`):** Always record the authenticated Zope username (`hr_manager`) from `getSecurityManager().getUser()` into both the entity row and `audit_logs`.
- **Two-phase rollback:** When creating an employee also writes an `audit_logs` row in the same request, `zope.sqlalchemy` guarantees that either **both** commit or **both** roll back.

---

## 6. Example Files & How to Run

### Files in `phase-5/`
- [run.bat](./run.bat) — one-click Windows launcher
- [pyproject.toml](./pyproject.toml) — defines `Zope[wsgi]`, `SQLAlchemy`, `PyMySQL`, `zope.sqlalchemy`
- [mysql_schema.sql](./mysql_schema.sql) — production-ready MySQL `utf8mb4` DDL (`employees` + `audit_logs`)
- [src/employee_api/db.py](./src/employee_api/db.py) — SQLAlchemy 2.x ORM models + `zope.sqlalchemy` registration + MySQL pool config
- [src/employee_api/security.py](./src/employee_api/security.py) — `acl_users` demo setup (`hr_manager`, `viewer`) + `getSecurityManager()` role helpers
- [src/employee_api/views.py](./src/employee_api/views.py) — role-protected SQL REST views + two-phase rollback demo
- [api.http](./api.http) — 10 clickable requests testing `401`, `403`, `200`, `201`, SQL rollback, and `/@@api-audit-logs`

### Quick Start (Windows)
```powershell
cd phase-5
.\run.bat
```

Open [api.http](./api.http) and click **Send Request** on requests 1 → 10!
