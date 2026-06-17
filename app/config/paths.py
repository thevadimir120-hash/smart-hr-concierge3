from __future__ import annotations

import os
from pathlib import Path

# Amvera: постоянное хранилище только в /data
DEFAULT_AMVERA_DB_URL = "sqlite+aiosqlite:////data/workora.db"
DEFAULT_LOCAL_DB_URL = "sqlite+aiosqlite:///./data/workora.db"


def get_database_url() -> str:
    """URL БД из окружения; на Amvera по умолчанию /data/workora.db."""
    return os.getenv("DATABASE_URL", DEFAULT_AMVERA_DB_URL).strip()


def get_persistence_dir() -> Path:
    """Каталог для SQLite и служебных файлов."""
    url = get_database_url()
    if "/data/" in url or url.endswith("/data/workora.db"):
        path = Path("/data")
    else:
        path = Path("data")
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_assets_dir() -> Path:
    """Каталог с изображениями вакансий (в репозитории, не в /data)."""
    path = Path(os.getenv("ASSETS_DIR", "assets"))
    path.mkdir(parents=True, exist_ok=True)
    return path
