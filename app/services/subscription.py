from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError

from app.config import Settings
from app.utils.retry import async_retry

logger = logging.getLogger(__name__)

SUBSCRIBED_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


class SubscriptionService:
    def __init__(self, bot: Bot, settings: Settings) -> None:
        self._bot = bot
        self._settings = settings

    async def is_subscribed(self, telegram_id: int) -> bool:
        async def _check() -> bool:
            member = await self._bot.get_chat_member(
                self._settings.channel_id,
                telegram_id,
            )
            return member.status in SUBSCRIBED_STATUSES

        try:
            return await async_retry(
                _check,
                attempts=3,
                delay=0.5,
                exceptions=(TelegramAPIError,),
            )
        except TelegramAPIError as exc:
            logger.error("Subscription check failed for %s: %s", telegram_id, exc)
            return False
