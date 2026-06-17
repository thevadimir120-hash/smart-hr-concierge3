from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            logger.info(
                "Message from %s: %s",
                event.from_user.id,
                (event.text or event.content_type)[:80],
            )
        elif isinstance(event, CallbackQuery) and event.from_user:
            logger.info(
                "Callback from %s: %s",
                event.from_user.id,
                event.data,
            )
        return await handler(event, data)
