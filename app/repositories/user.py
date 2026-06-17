from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self._session.execute(
            select(User).where(User.telegram_id == telegram_id),
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        username: str | None,
    ) -> User:
        user = User(telegram_id=telegram_id, username=username)
        self._session.add(user)
        await self._session.flush()
        return user

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None,
    ) -> tuple[User, bool]:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            if username and user.username != username:
                user.username = username
            return user, False
        user = await self.create(telegram_id, username)
        return user, True

    async def update_subscription(self, user: User, verified: bool) -> User:
        user.is_subscribed_verified = verified
        await self._session.flush()
        return user

    async def update_onboarding(
        self,
        user: User,
        city: str,
        work_format: str,
        desired_income: str | None = None,
    ) -> User:
        user.city = city
        user.desired_income = desired_income
        user.work_format = work_format
        user.onboarding_completed = True
        await self._session.flush()
        return user

    async def touch_activity(self, telegram_id: int) -> None:
        await self._session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(last_active_at=datetime.now(timezone.utc)),
        )

    async def count_all(self) -> int:
        result = await self._session.execute(select(func.count(User.id)))
        return int(result.scalar_one())

    async def count_active_since(self, days: int) -> int:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._session.execute(
            select(func.count(User.id)).where(User.last_active_at >= since),
        )
        return int(result.scalar_one())

    async def list_for_broadcast(self, only_onboarded: bool = True) -> list[User]:
        query = select(User).where(User.is_active.is_(True))
        if only_onboarded:
            query = query.where(User.onboarding_completed.is_(True))
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def list_inactive_since(self, days: int) -> list[User]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self._session.execute(
            select(User).where(
                User.is_active.is_(True),
                User.onboarding_completed.is_(True),
                User.last_active_at < since,
            ),
        )
        return list(result.scalars().all())
