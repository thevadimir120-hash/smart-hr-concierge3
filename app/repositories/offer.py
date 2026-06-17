from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer import Offer


class OfferRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, offer_id: int) -> Offer | None:
        result = await self._session.execute(select(Offer).where(Offer.id == offer_id))
        return result.scalar_one_or_none()

    async def list_active_by_category(self, category: str) -> list[Offer]:
        result = await self._session.execute(
            select(Offer)
            .where(Offer.category == category, Offer.is_active.is_(True))
            .order_by(Offer.sort_order, Offer.id),
        )
        return list(result.scalars().all())

    async def list_all(self) -> list[Offer]:
        result = await self._session.execute(
            select(Offer).order_by(Offer.category, Offer.sort_order, Offer.id),
        )
        return list(result.scalars().all())

    async def create(self, offer: Offer) -> Offer:
        self._session.add(offer)
        await self._session.flush()
        return offer

    async def update_referral_link(self, offer_id: int, link: str) -> Offer | None:
        offer = await self.get_by_id(offer_id)
        if not offer:
            return None
        offer.referral_link = link
        await self._session.flush()
        return offer

    async def set_active(self, offer_id: int, is_active: bool) -> Offer | None:
        offer = await self.get_by_id(offer_id)
        if not offer:
            return None
        offer.is_active = is_active
        await self._session.flush()
        return offer

    async def update_fields(self, offer_id: int, **fields: object) -> Offer | None:
        offer = await self.get_by_id(offer_id)
        if not offer:
            return None
        for key, value in fields.items():
            if hasattr(offer, key) and value is not None:
                setattr(offer, key, value)
        await self._session.flush()
        return offer

    async def deactivate_all_seed(self) -> None:
        await self._session.execute(update(Offer).values(is_active=False))
