from __future__ import annotations

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from app.bot_factory import create_bot, create_dispatcher
from app.config import get_settings, reset_settings_cache
from app.config.paths import get_assets_dir, get_persistence_dir
from app.database import get_database
from app.database.seed import seed_database
from app.repositories.settings import SettingsRepository
from app.scheduler import setup_scheduler
from app.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def _load_environment() -> None:
    """Локально подхватывает .env; на Amvera используются переменные панели."""
    load_dotenv(override=False)

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        logger.error("BOT_TOKEN не задан. Добавь переменную в Amvera или в .env")
        sys.exit(1)

    os.environ["BOT_TOKEN"] = bot_token
    if not os.getenv("DATABASE_URL", "").strip():
        from app.config.paths import get_database_url

        os.environ["DATABASE_URL"] = get_database_url()
    reset_settings_cache()


async def on_startup() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    persistence_dir = get_persistence_dir()
    assets_dir = get_assets_dir()
    logger.info("Persistence dir: %s", persistence_dir)
    logger.info("Assets dir: %s", assets_dir)

    db = get_database()
    await db.create_tables()

    async with db.session_factory() as session:
        await SettingsRepository(session).ensure_defaults()
        count = await seed_database(session)
        await session.commit()

    logger.info("Workora DB ready at %s, offers synced: %s", settings.database_url, count)


async def main() -> None:
    _load_environment()
    settings = get_settings()
    await on_startup()

    bot = create_bot(settings)
    dp = create_dispatcher(settings)
    db = get_database()

    scheduler = setup_scheduler(bot, settings, db.session_factory)
    scheduler.start()
    logger.info("APScheduler started (reminders, follow-ups, broadcasts)")

    try:
        logger.info("Workora bot started, polling...")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await db.dispose()
        await bot.session.close()
        logger.info("Workora bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
