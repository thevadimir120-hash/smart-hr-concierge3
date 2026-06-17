from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.click import Click
    from app.models.event import Event
    from app.models.offer_view import OfferView


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    desired_income: Mapped[str | None] = mapped_column(String(64), nullable=True)
    work_format: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_subscribed_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    clicks: Mapped[list[Click]] = relationship(back_populates="user", lazy="selectin")
    events: Mapped[list[Event]] = relationship(back_populates="user", lazy="selectin")
    offer_views: Mapped[list[OfferView]] = relationship(
        back_populates="user",
        lazy="selectin",
    )
