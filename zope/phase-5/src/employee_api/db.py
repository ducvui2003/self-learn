"""SQLAlchemy 2.x + zope.sqlalchemy integration for MySQL (with SQLite local fallback).

Spring Boot equivalent:
  - Spring Data JPA + Hibernate + HikariCP + MySQL Connector/J
  - `zope.sqlalchemy.register(Session)` hooks SQLAlchemy into Zope's per-request
    `transaction` manager (two-phase commit = automatic @Transactional across ZODB + MySQL!).

To use real MySQL, set the environment variable before running `run.bat`:
    set DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/zope_hr?charset=utf8mb4
If DATABASE_URL is not set, it falls back to local SQLite (`var/employees.db`)
so you can run and test immediately with zero DB setup.
"""

from datetime import datetime, timezone, timedelta
import os

from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker
import zope.sqlalchemy

JST = timezone(timedelta(hours=9))


def now_jst_iso():
    return datetime.now(JST).isoformat()


class Base(DeclarativeBase):
    pass


class EmployeeRecord(Base):
    """MySQL `employees` table (Japan-enterprise columns: soft delete, version, audit)."""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    emp_code = Column(String(20), unique=True, nullable=False, index=True)
    name_en = Column(String(100), nullable=False)
    name_ja = Column(String(100), nullable=False)
    department_en = Column(String(50), nullable=False, index=True)
    department_ja = Column(String(50), nullable=False)
    role = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False)

    # Japan-enterprise standard columns
    version = Column(Integer, nullable=False, default=1)
    deleted_flg = Column(Boolean, nullable=False, default=False)
    created_at = Column(String(40), nullable=False)
    created_by = Column(String(50), nullable=False)
    updated_at = Column(String(40), nullable=False)
    updated_by = Column(String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "empCode": self.emp_code,
            "nameEn": self.name_en,
            "nameJa": self.name_ja,
            "departmentEn": self.department_en,
            "departmentJa": self.department_ja,
            "role": self.role,
            "email": self.email,
            "version": self.version,
            "deletedFlg": bool(self.deleted_flg),
            "createdAt": self.created_at,
            "createdBy": self.created_by,
            "updatedAt": self.updated_at,
            "updatedBy": self.updated_by,
        }


class AuditLogRecord(Base):
    """MySQL `audit_logs` table (updated inside the SAME Zope transaction as `employees`)."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(50), nullable=False)
    emp_code = Column(String(20), nullable=False, index=True)
    actor = Column(String(50), nullable=False)
    detail = Column(String(255), nullable=False)
    created_at = Column(String(40), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "action": self.action,
            "empCode": self.emp_code,
            "actor": self.actor,
            "detail": self.detail,
            "createdAt": self.created_at,
        }


# Singleton engine + thread-local scoped_session (initialized lazily on first request)
_ENGINE = None
_DB_URL = None
DBSession = scoped_session(sessionmaker())
# Register DBSession with Zope's `transaction` manager (two-phase commit!)
zope.sqlalchemy.register(DBSession)


def get_database_url():
    """Return DATABASE_URL env var (MySQL) or default local SQLite file."""
    env_url = os.environ.get("DATABASE_URL", "").strip()
    if env_url:
        return env_url
    os.makedirs("var", exist_ok=True)
    return "sqlite:///var/employees.db"


def get_session():
    """Return the request-scoped SQLAlchemy session joined to Zope's transaction."""
    global _ENGINE, _DB_URL
    url = get_database_url()
    if _ENGINE is None or _DB_URL != url:
        engine_kwargs = {"pool_pre_ping": True}
        if url.startswith("mysql"):
            # MySQL connection pool tuning (like HikariCP in Spring Boot)
            engine_kwargs.update({"pool_size": 5, "max_overflow": 10, "pool_recycle": 1800})
        _ENGINE = create_engine(url, **engine_kwargs)
        _DB_URL = url
        DBSession.configure(bind=_ENGINE)
        Base.metadata.create_all(_ENGINE)
        _seed_if_empty()
    return DBSession()


def _seed_if_empty():
    """Seed initial Japan-enterprise employees once if the SQL table is empty."""
    session = DBSession()
    if session.query(EmployeeRecord).count() > 0:
        return
    now = now_jst_iso()
    seeds = [
        EmployeeRecord(
            emp_code="EMP-0001", name_en="Kenji Sato", name_ja="佐藤 健司",
            department_en="Sales", department_ja="営業部",
            role="Manager", email="k.sato@example.co.jp",
            version=1, deleted_flg=False,
            created_at=now, created_by="system", updated_at=now, updated_by="system",
        ),
        EmployeeRecord(
            emp_code="EMP-0002", name_en="Yuki Tanaka", name_ja="田中 由紀",
            department_en="Engineering", department_ja="開発部",
            role="Senior Backend Engineer", email="y.tanaka@example.co.jp",
            version=1, deleted_flg=False,
            created_at=now, created_by="system", updated_at=now, updated_by="system",
        ),
        EmployeeRecord(
            emp_code="EMP-0003", name_en="Haruka Suzuki", name_ja="鈴木 遥",
            department_en="HR", department_ja="人事部",
            role="HR Specialist", email="h.suzuki@example.co.jp",
            version=1, deleted_flg=False,
            created_at=now, created_by="system", updated_at=now, updated_by="system",
        ),
    ]
    session.add_all(seeds)
    session.flush()
