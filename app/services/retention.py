from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.models.event import EventType
from app.repositories.event import EventRepository
from app.repositories.offer import OfferRepository
from app.repositories.offer_view import OfferViewRepository
from app.repositories.settings import SettingsRepository
from app.repositories.user import UserRepository
from app.utils.retry import async_retry

logger = logging.getLogger(__name__)


class RetentionService:
    def __init__(self, session: AsyncSession, bot: Bot, settings: Settings) -> None:
        self._views = OfferViewRepository(session)
        self._users = UserRepository(session)
        self._offers = OfferRepository(session)
        self._events = EventRepository(session)
        self._settings_repo = SettingsRepository(session)
        self._bot = bot
        self._settings = settings

    async def send_offer_reminders(self) -> int:
        pending = await self._views.pending_reminders(self._settings.reminder_hours)
        reminder_text = await self._settings_repo.get_reminder_text()
        sent = 0
        for view in pending:
            user = await self._users.get_by_id(view.user_id)
            offer = await self._offers.get_by_id(view.offer_id)
            if not user or not offer:
                continue
            text = f"{reminder_text}\n\n<b>{offer.title}</b> — {offer.salary_info}"
            try:
                await async_retry(
                    lambda: self._bot.send_message(
                        user.telegram_id,
                        text,
                        parse_mode="HTML",
                    ),
                    attempts=2,
                    exceptions=(TelegramAPIError,),
                )
                await self._views.mark_reminder_sent(view.id)
                await self._events.log(user.id, EventType.REMINDER_SENT, str(offer.id))
                sent += 1
            except TelegramAPIError as exc:
                logger.warning("Reminder failed for %s: %s", user.telegram_id, exc)
        return sent

    async def send_click_followups(self, minutes: int = 30) -> int:
        pending = await self._views.pending_followup_30(minutes)
        followup_text = await self._settings_repo.get_followup_30_text()
        sent = 0
        for view in pending:
            user = await self._users.get_by_id(view.user_id)
            offer = await self._offers.get_by_id(view.offer_id)
            if not user or not offer or offer.is_paused:
                continue
            try:
                from app.keyboards.offers import offer_card_keyboard

                await async_retry(
                    lambda: self._bot.send_message(
                        user.telegram_id,
                        followup_text,
                        parse_mode="HTML",
                        reply_markup=offer_card_keyboard(offer),
                    ),
                    attempts=2,
                    exceptions=(TelegramAPIError,),
                )
                await self._views.mark_followup_30_sent(view.id)
                await self._events.log(user.id, EventType.FOLLOWUP_30_SENT, str(offer.id))
                sent += 1
            except TelegramAPIError as exc:
                logger.warning("Followup failed for %s: %s", user.telegram_id, exc)
        return sent

    async def send_reengagement(self) -> int:
        inactive = await self._users.list_inactive_since(self._settings.reengagement_days)
        text = (
            "Давно не заходил! В каталоге появились новые вакансии с гибким графиком "
            "и повышенной оплатой на этой неделе.\n\n"
            "Нажми /menu — подберу актуальные варианты."
        )
        sent = 0
        for user in inactive:
            try:
                await self._bot.send_message(user.telegram_id, text)
                await self._events.log(user.id, EventType.REENGAGEMENT_SENT)
                await self._users.touch_activity(user.telegram_id)
                sent += 1
            except TelegramAPIError as exc:
                logger.warning("Reengagement failed for %s: %s", user.telegram_id, exc)
        return sent
