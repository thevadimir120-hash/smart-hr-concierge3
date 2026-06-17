from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.click import Click
    from app.models.offer_view import OfferView


class OfferCategory(StrEnum):
    BANKING = "banking"
    DELIVERY = "delivery"
    JOBS = "jobs"
    REMOTE = "remote"
    BEGINNER = "beginner"


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)
    short_description: Mapped[str] = mapped_column(Text)
    benefits: Mapped[str] = mapped_column(Text)
    salary_info: Mapped[str] = mapped_column(String(255))
    bonuses: Mapped[str | None] = mapped_column(String(512), default="", nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    referral_link: Mapped[str] = mapped_column(String(1024))
    payout: Mapped[float | None] = mapped_column(Float, nullable=True)
    cta_text: Mapped[str] = mapped_column(String(128), default="🚀 Занять рабочее место")
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True, index=True, nullable=True)
    is_paused: Mapped[bool | None] = mapped_column(Boolean, default=False, nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    clicks: Mapped[list[Click]] = relationship(back_populates="offer", lazy="selectin")
    offer_views: Mapped[list[OfferView]] = relationship(
        back_populates="offer",
        lazy="selectin",
    )