from __future__ import annotations

import os
from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.paths import get_database_url
from app.config import get_settings
from app.database.base import Base


def _register_sqlite_pragmas(engine: AsyncEngine) -> None:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


class Database:
    def __init__(self, url: str) -> None:
        engine_kwargs: dict = {"echo": False, "future": True}
        if url.startswith("sqlite"):
            engine_kwargs["connect_args"] = {"timeout": 30}

        self.engine: AsyncEngine = create_async_engine(url, **engine_kwargs)

        if url.startswith("sqlite"):
            _register_sqlite_pragmas(self.engine)

        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def create_tables(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


_database: Database | None = None


def get_database() -> Database:
    global _database
    if _database is None:
        url = os.getenv("DATABASE_URL") or get_settings().database_url or get_database_url()
        _database = Database(url)
    return _database
