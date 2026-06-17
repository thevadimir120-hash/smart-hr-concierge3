from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer import Offer
from app.repositories.offer import OfferRepository
from app.repositories.settings import SettingsRepository
from app.services.analytics import AnalyticsService


class AdminService:
    def __init__(self, session: AsyncSession) -> None:
        self._settings = SettingsRepository(session)
        self._offers = OfferRepository(session)
        self._analytics = AnalyticsService(session)

    @property
    def analytics(self) -> AnalyticsService:
        return self._analytics

    async def get_welcome_text(self) -> str:
        return await self._settings.get_welcome_text()

    async def set_welcome_text(self, text: str) -> None:
        await self._settings.set(SettingsRepository.WELCOME_KEY, text)

    async def list_offers(self) -> list[Offer]:
        return await self._offers.list_all()

    async def toggle_offer(self, offer_id: int) -> Offer | None:
        offer = await self._offers.get_by_id(offer_id)
        if not offer:
            return None
        return await self._offers.set_active(offer_id, not offer.is_active)

    async def update_referral_link(self, offer_id: int, link: str) -> Offer | None:
        return await self._offers.update_referral_link(offer_id, link.strip())

    async def create_offer(self, offer: Offer) -> Offer:
        return await self._offers.create(offer)
