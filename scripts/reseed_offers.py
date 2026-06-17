"""Перезалить полный каталог профессий в базу (заменяет старые офферы)."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from app.database import get_database
from app.services.seed import reseed_all_offers


async def main() -> None:
    load_dotenv(ROOT / ".env")
    db = get_database()
    await db.create_tables()
    async with db.session_factory() as session:
        count = await reseed_all_offers(session)
        await session.commit()
    print(f"Готово: загружено {count} офферов с полными описаниями.")


if __name__ == "__main__":
    asyncio.run(main())
