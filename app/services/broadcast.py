from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import EventType
from app.repositories.event import EventRepository
from app.repositories.user import UserRepository
from app.utils.retry import async_retry

logger = logging.getLogger(__name__)


class BroadcastService:
    def __init__(self, session: AsyncSession, bot: Bot) -> None:
        self._users = UserRepository(session)
        self._events = EventRepository(session)
        self._bot = bot

    async def send_to_all(
        self,
        text: str,
        *,
        only_onboarded: bool = True,
        parse_mode: str = "HTML",
    ) -> tuple[int, int]:
        users = await self._users.list_for_broadcast(only_onboarded=only_onboarded)
        success = 0
        failed = 0
        for user in users:
            telegram_id = user.telegram_id

            async def _send(tid: int = telegram_id) -> None:
                await self._bot.send_message(tid, text, parse_mode=parse_mode)

            try:
                await async_retry(
                    _send,
                    attempts=2,
                    delay=0.3,
                    exceptions=(TelegramAPIError,),
                )
                await self._events.log(user.id, EventType.BROADCAST_RECEIVED)
                success += 1
            except TelegramAPIError as exc:
                logger.warning("Broadcast failed for %s: %s", user.telegram_id, exc)
                failed += 1
            await asyncio.sleep(0.05)
        return success, failed
