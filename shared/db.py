"""
Database engine + session factory for all Hoku AI modules.

Reads DATABASE_URL from shared.config. The SAME code runs against:
  - a local SQLite file for dev testing   (DATABASE_URL=sqlite:///./hoku_local.db)
  - Talha's production PostgreSQL          (DATABASE_URL=postgresql://.../hoku_health)
Only the URL in .env changes — no code changes between the two.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from shared.config import settings

# SQLite needs this arg to allow use across threads; Postgres does not.
_connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,  # drop dead connections instead of erroring mid-request
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# All ORM models inherit from this Base.
Base = declarative_base()
