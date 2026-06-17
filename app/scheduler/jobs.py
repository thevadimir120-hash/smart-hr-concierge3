from __future__ import annotations

import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Settings
from app.services.broadcast import BroadcastService
from app.services.retention import RetentionService

logger = logging.getLogger(__name__)

WEEKLY_BROADCAST_TEXT = (
    "<b>Еженедельная подборка Workora</b>\n\n"
    "На этой неделе открылись новые слоты в доставке и на удаленке. "
    "Загляни в каталог — /menu"
)

BONUS_NOTIFICATION_TEXT = (
    "🔥 <b>Повышенная оплата на этой неделе</b>\n\n"
    "Несколько компаний подняли ставки за смены и оформление. "
    "Проверь каталог, пока места еще есть."
)

PAYOUT_NOTIFICATION_TEXT = (
    "📈 <b>Горячие вакансии сегодня</b>\n\n"
    "В категориях «Доставка» и «Банковские продукты» открыты позиции "
    "с повышенным доходом. Жми /menu."
)


def _parse_cron(cron: str) -> CronTrigger:
    minute, hour, day, month, day_of_week = cron.split()
    return CronTrigger(
        minute=minute,
        hour=hour,
        day=day,
        month=month,
        day_of_week=day_of_week,
    )


def setup_scheduler(
    bot: Bot,
    settings: Settings,
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")

    async def run_reminders() -> None:
        try:
            async with session_factory() as session:
                service = RetentionService(session, bot, settings)
                sent = await service.send_offer_reminders()
                await session.commit()
                logger.info("2h reminders sent: %s", sent)
        except Exception:
            logger.exception("run_reminders failed")

    async def run_followup_30() -> None:
        try:
            async with session_factory() as session:
                service = RetentionService(session, bot, settings)
                sent = await service.send_click_followups(settings.followup_minutes)
                await session.commit()
                logger.info("30min followups sent: %s", sent)
        except Exception:
            logger.exception("run_followup_30 failed")

    async def run_reengagement() -> None:
        try:
            async with session_factory() as session:
                service = RetentionService(session, bot, settings)
                sent = await service.send_reengagement()
                await session.commit()
                logger.info("Reengagement sent: %s", sent)
        except Exception:
            logger.exception("run_reengagement failed")

    async def run_weekly_broadcast() -> None:
        try:
            async with session_factory() as session:
                service = BroadcastService(session, bot)
                success, failed = await service.send_to_all(WEEKLY_BROADCAST_TEXT)
                await session.commit()
                logger.info("Weekly broadcast: ok=%s fail=%s", success, failed)
        except Exception:
            logger.exception("weekly broadcast failed")

    async def run_bonus_broadcast() -> None:
        try:
            async with session_factory() as session:
                service = BroadcastService(session, bot)
                success, failed = await service.send_to_all(BONUS_NOTIFICATION_TEXT)
                await session.commit()
                logger.info("Bonus broadcast: ok=%s fail=%s", success, failed)
        except Exception:
            logger.exception("bonus broadcast failed")

    async def run_payout_broadcast() -> None:
        try:
            async with session_factory() as session:
                service = BroadcastService(session, bot)
                success, failed = await service.send_to_all(PAYOUT_NOTIFICATION_TEXT)
                await session.commit()
                logger.info("Payout broadcast: ok=%s fail=%s", success, failed)
        except Exception:
            logger.exception("payout broadcast failed")

    scheduler.add_job(
        run_reminders,
        trigger=IntervalTrigger(minutes=15),
        id="offer_reminders",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_followup_30,
        trigger=IntervalTrigger(minutes=5),
        id="followup_30",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_reengagement,
        trigger=IntervalTrigger(hours=24),
        id="reengagement",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_weekly_broadcast,
        trigger=_parse_cron(settings.weekly_broadcast_cron),
        id="weekly_broadcast",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_bonus_broadcast,
        trigger=_parse_cron(settings.bonus_notification_cron),
        id="bonus_broadcast",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.add_job(
        run_payout_broadcast,
        trigger=_parse_cron(settings.payout_notification_cron),
        id="payout_broadcast",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    return scheduler
