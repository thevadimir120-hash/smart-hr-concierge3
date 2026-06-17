from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import EventType
from app.repositories.click import ClickRepository
from app.repositories.event import EventRepository
from app.repositories.offer import OfferRepository
from app.repositories.user import UserRepository


@dataclass(frozen=True)
class DailyStats:
    new_users: int
    clicks: int
    registrations: int
    active_users: int
    conversion_rate: float


@dataclass(frozen=True)
class FullStats:
    total_users: int
    total_clicks: int
    total_registrations: int
    active_users_7d: int
    conversion_rate: float
    top_offers: list[tuple[str, int]]


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)
        self._clicks = ClickRepository(session)
        self._events = EventRepository(session)
        self._offers = OfferRepository(session)

    async def daily_stats(self) -> DailyStats:
        clicks = await self._clicks.count_since(1)
        registrations = await self._events.count_by_type_since(
            EventType.REGISTRATION,
            1,
        )
        active = await self._users.count_active_since(1)
        new_users = active
        conversion = (registrations / clicks * 100) if clicks else 0.0
        return DailyStats(
            new_users=new_users,
            clicks=clicks,
            registrations=registrations,
            active_users=active,
            conversion_rate=round(conversion, 2),
        )

    async def full_stats(self) -> FullStats:
        total_users = await self._users.count_all()
        total_clicks = await self._clicks.count_all()
        total_registrations = await self._events.count_by_type(EventType.REGISTRATION)
        active_7d = await self._users.count_active_since(7)
        conversion = (
            (total_registrations / total_clicks * 100) if total_clicks else 0.0
        )
        top = await self._clicks.top_offers(5)
        offer_titles: list[tuple[str, int]] = []
        for offer_id, count in top:
            offer = await self._offers.get_by_id(offer_id)
            title = offer.title if offer else f"Offer #{offer_id}"
            offer_titles.append((title, count))
        return FullStats(
            total_users=total_users,
            total_clicks=total_clicks,
            total_registrations=total_registrations,
            active_users_7d=active_7d,
            conversion_rate=round(conversion, 2),
            top_offers=offer_titles,
        )

    def format_daily(self, stats: DailyStats) -> str:
        return (
            "<b>📊 Статистика за сегодня</b>\n\n"
            f"Активных пользователей: <b>{stats.active_users}</b>\n"
            f"Кликов по офферам: <b>{stats.clicks}</b>\n"
            f"Регистраций: <b>{stats.registrations}</b>\n"
            f"Конверсия: <b>{stats.conversion_rate}%</b>"
        )

    def format_full(self, stats: FullStats) -> str:
        top_lines = "\n".join(
            f"• {title}: {count} кликов" for title, count in stats.top_offers
        ) or "• Пока нет данных"
        return (
            "<b>📈 Общая аналитика</b>\n\n"
            f"Всего пользователей: <b>{stats.total_users}</b>\n"
            f"Активных за 7 дней: <b>{stats.active_users_7d}</b>\n"
            f"Всего кликов: <b>{stats.total_clicks}</b>\n"
            f"Регистраций: <b>{stats.total_registrations}</b>\n"
            f"Конверсия: <b>{stats.conversion_rate}%</b>\n\n"
            f"<b>Топ офферов:</b>\n{top_lines}"
        )
