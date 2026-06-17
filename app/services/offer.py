from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.config.paths import get_assets_dir
from app.models.event import EventType
from app.models.offer import Offer, OfferCategory
from app.repositories.click import ClickRepository
from app.repositories.event import EventRepository
from app.repositories.offer import OfferRepository
from app.repositories.offer_view import OfferViewRepository
from app.repositories.user import UserRepository
from app.utils.text import format_offer_card

logger = logging.getLogger(__name__)


class OfferService:
    def __init__(self, session: AsyncSession) -> None:
        self._offers = OfferRepository(session)
        self._clicks = ClickRepository(session)
        self._views = OfferViewRepository(session)
        self._events = EventRepository(session)
        self._users = UserRepository(session)

    async def list_active_by_category(self, category: str) -> list[Offer]:
        offers = await self._offers.list_active_by_category(category)
        if category == OfferCategory.BEGINNER:
            return offers
        return [o for o in offers if not o.is_paused]

    async def get_offer(self, offer_id: int) -> Offer | None:
        return await self._offers.get_by_id(offer_id)

    async def open_offer(
        self,
        telegram_id: int,
        offer_id: int,
    ) -> tuple[Offer | None, str]:
        user = await self._users.get_by_telegram_id(telegram_id)
        offer = await self._offers.get_by_id(offer_id)
        if not user or not offer or not offer.is_active:
            return offer, ""
        await self._views.record_view(user.id, offer_id)
        await self._events.log(
            user.id,
            EventType.OFFER_VIEWED,
            payload=str(offer_id),
        )
        return offer, format_offer_card(offer)

    async def track_category_view(self, telegram_id: int, category: str) -> None:
        user = await self._users.get_by_telegram_id(telegram_id)
        if user:
            await self._events.log(
                user.id,
                EventType.CATEGORY_VIEWED,
                payload=category,
            )

    async def track_referral_click(self, telegram_id: int, offer_id: int) -> None:
        user = await self._users.get_by_telegram_id(telegram_id)
        if not user:
            return
        if not await self._clicks.has_clicked(user.id, offer_id):
            await self._clicks.record(user.id, offer_id)
        await self._views.mark_clicked(user.id, offer_id)
        await self._events.log(
            user.id,
            EventType.REFERRAL_CLICKED,
            payload=str(offer_id),
        )

    def resolve_image(self, offer: Offer, base_dir: Path | None = None) -> Path | None:
        if not offer.image_path:
            return None
        root = base_dir or get_assets_dir()
        rel = offer.image_path.removeprefix("assets/").removeprefix("assets\\")
        candidates = [
            root / rel,
            root / offer.image_path,
            Path(offer.image_path),
        ]
        for path in candidates:
            if path.is_file():
                return path
            for ext in (".jpg", ".jpeg", ".png", ".webp"):
                alt = path.with_suffix(ext) if path.suffix else Path(str(path) + ext)
                if alt.is_file():
                    return alt
        logger.debug("Image not found for offer %s: %s", offer.id, offer.image_path)
        return None
