"""Database configuration with safe in-memory defaults.

This module provides minimal, working SQLAlchemy async setup using an
in-memory SQLite database. It is intended to avoid import/runtime errors
in fresh template projects and CI pipelines. Projects can replace this
with their real database configuration without changing import sites.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy base model class."""


# Use in-memory SQLite for a zero-dependency, CI-friendly default.
# This keeps the app importable and tests runnable without external services.
_ENGINE: AsyncEngine | None = None
_SessionLocal: async_sessionmaker[AsyncSession] | None = None


def _ensure_engine() -> None:
    global _ENGINE, _SessionLocal
    if _ENGINE is None:
        # Lazy import aiosqlite driver; installation is declared in pyproject
        _ENGINE = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
        _SessionLocal = async_sessionmaker(
            bind=_ENGINE, expire_on_commit=False, autoflush=False, autocommit=False
        )


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async SQLAlchemy session.

    Uses an in-memory SQLite database by default so imports and basic
    operations succeed in CI even without a real DB. Replace this in your
    project to point at your actual database.
    """
    _ensure_engine()
    # Guard for type checkers and runtime without using assert (Bandit B101)
    if _SessionLocal is None:  # pragma: no cover
        raise RuntimeError("Database session factory not initialized")
    async with _SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Initialize database (no-op for in-memory default)."""
    _ensure_engine()
