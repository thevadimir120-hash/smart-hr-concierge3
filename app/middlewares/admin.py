from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.config import get_settings


class AdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = None
        if isinstance(event, (Message, CallbackQuery)) and event.from_user:
            user_id = event.from_user.id
        if user_id is None or user_id not in get_settings().admin_ids:
            if isinstance(event, CallbackQuery):
                await event.answer("Доступ запрещён", show_alert=True)
            elif isinstance(event, Message):
                await event.answer("У вас нет прав администратора.")
            return None
        data["is_admin"] = True
        return await handler(event, data)
