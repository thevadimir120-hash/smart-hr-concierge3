from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

from app.config import Settings, get_settings
from app.handlers import setup_routers
from app.handlers.admin import admin_router
from app.middlewares import (
    AdminMiddleware,
    DatabaseMiddleware,
    LoggingMiddleware,
    ThrottlingMiddleware,
)

logger = logging.getLogger(__name__)


def create_bot(settings: Settings | None = None) -> Bot:
    cfg = settings or get_settings()
    return Bot(
        token=cfg.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher(settings: Settings | None = None) -> Dispatcher:
    _ = settings
    dp = Dispatcher(storage=MemoryStorage())

    admin_router.message.middleware(AdminMiddleware())
    admin_router.callback_query.middleware(AdminMiddleware())

    dp.update.middleware(LoggingMiddleware())
    dp.update.middleware(ThrottlingMiddleware())
    dp.update.middleware(DatabaseMiddleware())
    dp.include_router(setup_routers())

    @dp.errors()
    async def errors_handler(event: ErrorEvent) -> None:
        logger.exception("Unhandled error: %s", event.exception)

    return dp
