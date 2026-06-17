from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer_view import OfferView


class OfferViewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_view(self, user_id: int, offer_id: int) -> OfferView:
        result = await self._session.execute(
            select(OfferView).where(
                OfferView.user_id == user_id,
                OfferView.offer_id == offer_id,
            ),
        )
        view = result.scalar_one_or_none()
        if view:
            view.viewed_at = datetime.now(timezone.utc)
            view.followup_30_sent = False
            await self._session.flush()
            return view
        view = OfferView(user_id=user_id, offer_id=offer_id)
        self._session.add(view)
        await self._session.flush()
        return view

    async def mark_clicked(self, user_id: int, offer_id: int) -> None:
        result = await self._session.execute(
            select(OfferView).where(
                OfferView.user_id == user_id,
                OfferView.offer_id == offer_id,
            ),
        )
        view = result.scalar_one_or_none()
        if view:
            view.clicked = True
            await self._session.flush()

    async def mark_reminder_sent(self, view_id: int) -> None:
        await self._session.execute(
            update(OfferView)
            .where(OfferView.id == view_id)
            .values(reminder_sent=True),
        )

    async def mark_followup_30_sent(self, view_id: int) -> None:
        await self._session.execute(
            update(OfferView)
            .where(OfferView.id == view_id)
            .values(followup_30_sent=True),
        )

    async def pending_reminders(self, hours: int) -> list[OfferView]:
        threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
        result = await self._session.execute(
            select(OfferView).where(
                OfferView.clicked.is_(False),
                OfferView.reminder_sent.is_(False),
                OfferView.followup_30_sent.is_(False),
                OfferView.viewed_at <= threshold,
            ),
        )
        return list(result.scalars().all())

    async def pending_followup_30(self, minutes: int) -> list[OfferView]:
        threshold = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        result = await self._session.execute(
            select(OfferView).where(
                OfferView.followup_30_sent.is_(False),
                OfferView.viewed_at <= threshold,
            ),
        )
        return list(result.scalars().all())
