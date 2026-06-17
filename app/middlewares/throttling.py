from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.config import get_settings


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self._last_event: dict[int, float] = {}
        self._rate = get_settings().flood_rate_limit

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = self._extract_user_id(event)
        if user_id is None:
            return await handler(event, data)

        now = time.monotonic()
        last = self._last_event.get(user_id, 0.0)
        if now - last < self._rate:
            if isinstance(event, CallbackQuery):
                await event.answer("Подождите секунду…", show_alert=False)
            return None

        self._last_event[user_id] = now
        return await handler(event, data)

    @staticmethod
    def _extract_user_id(event: TelegramObject) -> int | None:
        if isinstance(event, Message) and event.from_user:
            return event.from_user.id
        if isinstance(event, CallbackQuery) and event.from_user:
            return event.from_user.id
        return None
