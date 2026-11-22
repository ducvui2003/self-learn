# Phase 2 — ZODB, Persistence, ACID Transactions & Acquisition

Goal: understand how **ZODB** (Zope Object Database) stores Python objects directly on disk, how Zope manages **ACID transactions** per HTTP request, and how **Acquisition** works (and its pitfalls).

> **Note for MySQL developers:** Even when your business tables live in **MySQL** (covered in Phase 5), Zope **still uses ZODB** internally for its own object tree (root `/`, folders, `acl_users`, ZMI objects, app settings). Understanding ZODB and Acquisition is essential for reading any Zope codebase.

---

## 1. ZODB & Persistent Objects (Java Spring/JPA vs Zope)

In Spring Data JPA, you map Java `@Entity` classes to MySQL rows via Hibernate.
In Zope, **ZODB** saves real Python object graphs directly into `var/Data.fs` (no SQL, no ORM mapping).

| Concept | Java Spring + JPA / MySQL | Zope 5 + ZODB |
| :--- | :--- | :--- |
| Persistent entity | `@Entity` class | Subclass of `persistent.Persistent` (or `OFS.SimpleItem.SimpleItem`) |
| Container / table | SQL table + `JpaRepository` | `OFS.Folder.Folder` + `BTrees.OOBTree.OOBTree` |
| Indexed lookup | B-Tree primary key index | `OOBTree` (Object key -> Object value, O(log N) lookup) |
| Storage file | MySQL `.ibd` tablespace | `var/Data.fs` (FileStorage) |
| Save / update | `repository.save(entity)` | Just mutate attributes on a `Persistent` object — saved automatically at request end |
| Tracked list/map | Hibernate `PersistentBag` | `persistent.list.PersistentList` / `persistent.mapping.PersistentMapping` |

### Why `OOBTree` instead of a plain `dict`?
- A plain Python `dict` inside ZODB loads **every entry** into RAM at once and rewrites the whole `dict` on any change.
- An **`OOBTree`** splits entries into small buckets on disk — ZODB only loads and saves the buckets you touch (just like a B-Tree index in MySQL).

---

## 2. The `_p_changed` Mutability Pitfall (CRITICAL!)

ZODB detects changes automatically when you **assign** an attribute directly on a `Persistent` object:
```python
emp.role = "Tech Lead"          # ✅ ZODB sees __setattr__ -> saved!
```

**HOWEVER**, if you mutate a plain Python `list` or `dict` in place, ZODB does **NOT** notice:
```python
# ❌ BUG: plain list mutation is NOT detected by ZODB!
self.skills = ["Python"]
emp.skills.append("Zope")       # Lost after restart!
```

### Two safe fixes:
1. **Recommended:** Use `PersistentList` (or `PersistentMapping`):
   ```python
   from persistent.list import PersistentList
   self.skills = PersistentList(["Python"])
   emp.skills.append("Zope")    # ✅ Automatically persisted!
   ```
2. **Manual flag:** Tell ZODB explicitly that the object changed:
   ```python
   emp.skills.append("Zope")
   emp._p_changed = True        # ✅ Forces ZODB to save `emp`
   ```

---

## 3. Automatic ACID Transactions per Request

In Spring, you put `@Transactional` on a service method.
In Zope, **every HTTP request automatically runs inside an ACID transaction** managed by the `transaction` package:

| Behavior | Java Spring `@Transactional` | Zope 5 `transaction` |
| :--- | :--- | :--- |
| Start transaction | Entering `@Transactional` method | Automatically at HTTP request start |
| Commit | Method returns normally | Automatically at HTTP request end (`transaction.commit()`) |
| Rollback | Unchecked exception thrown | Unhandled exception **or** explicit `transaction.abort()` |
| Optimistic locking | `@Version` -> `OptimisticLockException` | ZODB `ConflictError` (Zope **auto-retries** the request up to 3 times!) |
| Sync with MySQL | JTA / single datasource | `zope.sqlalchemy` joins the **same** Zope transaction (Phase 5!) |

In our example (`POST /api-employees?simulateError=true`), we insert an `Employee` into ZODB and then call `transaction.abort()` — proving the insert is completely rolled back.

---

## 4. Acquisition (Unique to Zope!)

**Acquisition** means a child object inside a folder can **inherit attributes, methods, and security rules from its parent folders** (like dynamic context inheritance).

In our Phase 2 example:
- `EmployeeFolder` defines `company_name = "Tokyo Tech Corp (東京テック株式会社)"`.
- `Employee` does **NOT** have `company_name` on itself.
- When `Employee` is wrapped in its parent folder (`emp.__of__(folder)`):
  - `getattr(emp, "company_name")` → walks up to `EmployeeFolder` and returns `"Tokyo Tech Corp (東京テック株式会社)"`!
  - `hasattr(aq_base(emp), "company_name")` → `aq_base()` strips the Acquisition wrapper and checks **only** `emp`'s own attributes → returns `False`!

| Helper (`from Acquisition import ...`) | What it does |
| :--- | :--- |
| `obj.__of__(parent)` | Wraps `obj` inside `parent`'s Acquisition context |
| `aq_parent(obj)` | Returns the parent object in the Acquisition chain |
| `aq_base(obj)` | **Strips Acquisition** — returns the raw object (use this before `hasattr`/`getattr` checks!) |

---

## 5. Common Pitfalls

1. **Mutating plain `list`/`dict` on a `Persistent` object:** Always use `PersistentList`/`PersistentMapping` or set `obj._p_changed = True`.
2. **Storing non-picklable objects in ZODB:** Never store open DB connections, sockets, or lambdas as attributes on a `Persistent` object — ZODB pickles attributes to `Data.fs`. (Use `_v_` prefix like `_v_cache` for volatile in-memory attributes that ZODB ignores.)
3. **Accidental Acquisition lookup (`hasattr(obj, "foo")`):** Because of Acquisition, `hasattr(child, "foo")` can unexpectedly return `True` if a parent folder has `"foo"`. Always use `hasattr(aq_base(child), "foo")` when checking an object's own attributes.
4. **Calling `transaction.commit()` manually in views:** Almost never needed — let Zope commit automatically at the end of the HTTP request so ZODB and MySQL stay in sync.
5. **Forgetting to wrap objects fetched from `OOBTree`:** Unlike `folder["child"]`, `OOBTree.get(key)` does **not** auto-wrap Acquisition. Call `emp.__of__(folder)` when you need parent Acquisition.
6. **`DELETE` / `PUT` returning `404` (`webdav.NullResource`):** Zope treats `PUT` and `DELETE` on folder paths as WebDAV methods by default, so `/api-employees/EMP-0004` gets intercepted before reaching `<browser:page>`. Use the `@@` view prefix (`/@@api-employees/EMP-0004`) to bypass WebDAV, or use a custom traverser / `plone.rest` (covered in Phase 4).

---

## 6. Japan-Project Tips

- **Soft delete (`deleted_flg`) & audit columns:** Even in ZODB (and later MySQL), Japan enterprise systems normally use logical delete (`deleted_flg = True`, `updated_at`, `updated_by`) instead of hard `del` so audit history stays intact.
- **ZODB `Data.fs` grows over time:** Because ZODB is append-only (to support the ZMI **Undo** tab), production ops teams run periodic **packing** (`zopectl` / ZMI Database Management -> Pack) via cron to reclaim disk space.
- **Legacy Zope 2 note:** Older Zope 2 projects often store hundreds of custom objects directly inside `OFS.Folder` (not `OOBTree`) and rely heavily on Acquisition for templates and `ZSQLMethods`. Knowing `aq_base()` and `aq_parent()` will save you hours when debugging legacy code.

---

## 7. Example Files & How to Run

### Files in `phase-2/`
- [run.bat](./run.bat) — one-click Windows launcher (uses shared `..\.venv`, installs Phase 2 `employee_api`, starts Zope 5)
- [pyproject.toml](./pyproject.toml) — defines `Zope[wsgi]>=5.13,<6.0`
- [src/employee_api/models.py](./src/employee_api/models.py) — `Employee` (`SimpleItem`, `PersistentList`, `aq_base`) and `EmployeeFolder` (`Folder`, `OOBTree`, Acquisition)
- [src/employee_api/storage.py](./src/employee_api/storage.py) — initializes `employees_store` in ZODB with 3 Japan-enterprise employees
- [src/employee_api/views.py](./src/employee_api/views.py) — REST API supporting `GET`, `POST`, `DELETE`, `PersistentList` skill updates, and ACID rollback demo
- [src/employee_api/configure.zcml](./src/employee_api/configure.zcml) — registers `/api-health` and `/api-employees`
- [api.http](./api.http) — 10 clickable test requests (CRUD, Acquisition, `PersistentList`, 409 duplicate, ACID rollback, soft delete)

### Quick Start (Windows)
```powershell
cd phase-2
.\run.bat
```

### Cross-Platform Setup (macOS / Linux / CI)
```bash
# From zope/
.venv/bin/python -m pip install -e ./phase-2
cd phase-2
mkdir -p var
../.venv/bin/runwsgi -v etc/zope.ini
```

### Test the API
Open [api.http](./api.http) and click **Send Request** on requests 1 → 10 in order, or try stopping and restarting `run.bat` after creating `EMP-0004` to see it persist in `var/Data.fs`!
