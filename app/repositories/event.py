from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event, EventType


class EventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log(
        self,
        user_id: int,
        event_type: EventType | str,
        payload: str | None = None,
    ) -> Event:
        event = Event(
            user_id=user_id,
            event_type=str(event_type),
            payload=payload,
        )
        self._session.add(event)
        await self._session.flush()
        return event

    async def count_by_type(self, event_type: EventType | str) -> int:
        result = await self._session.execute(
            select(func.count(Event.id)).where(Event.event_type == str(event_type)),
        )
        return int(result.scalar_one())

    async def count_by_type_since(
        self,
        event_type: EventType | str,
        days: int,
    ) -> int:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._session.execute(
            select(func.count(Event.id)).where(
                Event.event_type == str(event_type),
                Event.timestamp >= since,
            ),
        )
        return int(result.scalar_one())
