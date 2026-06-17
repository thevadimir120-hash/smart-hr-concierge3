from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import EventType
from app.models.user import User
from app.repositories.event import EventRepository
from app.repositories.user import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._users = UserRepository(session)
        self._events = EventRepository(session)

    async def register_start(
        self,
        telegram_id: int,
        username: str | None,
    ) -> tuple[User, bool]:
        user, created = await self._users.get_or_create(telegram_id, username)
        await self._events.log(user.id, EventType.START)
        await self._users.touch_activity(telegram_id)
        return user, created

    async def mark_subscribed(self, user: User) -> User:
        user = await self._users.update_subscription(user, True)
        await self._events.log(user.id, EventType.SUBSCRIPTION_VERIFIED)
        return user

    async def complete_onboarding(
        self,
        user: User,
        city: str,
        time_commitment: str,
    ) -> User:
        user = await self._users.update_onboarding(
            user,
            city=city.strip(),
            desired_income=None,
            work_format=time_commitment,
        )
        await self._events.log(user.id, EventType.ONBOARDING_COMPLETED)
        return user

    async def touch(self, telegram_id: int) -> None:
        await self._users.touch_activity(telegram_id)
