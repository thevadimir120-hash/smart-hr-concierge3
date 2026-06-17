from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.click import Click


class ClickRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(self, user_id: int, offer_id: int) -> Click:
        click = Click(user_id=user_id, offer_id=offer_id)
        self._session.add(click)
        await self._session.flush()
        return click

    async def has_clicked(self, user_id: int, offer_id: int) -> bool:
        result = await self._session.execute(
            select(Click.id).where(
                Click.user_id == user_id,
                Click.offer_id == offer_id,
            ).limit(1),
        )
        return result.scalar_one_or_none() is not None

    async def count_all(self) -> int:
        result = await self._session.execute(select(func.count(Click.id)))
        return int(result.scalar_one())

    async def count_since(self, days: int) -> int:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._session.execute(
            select(func.count(Click.id)).where(Click.clicked_at >= since),
        )
        return int(result.scalar_one())

    async def top_offers(self, limit: int = 5) -> list[tuple[int, int]]:
        result = await self._session.execute(
            select(Click.offer_id, func.count(Click.id).label("cnt"))
            .group_by(Click.offer_id)
            .order_by(func.count(Click.id).desc())
            .limit(limit),
        )
        return [(int(row[0]), int(row[1])) for row in result.all()]
