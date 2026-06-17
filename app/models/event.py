from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class EventType(StrEnum):
    START = "start"
    SUBSCRIPTION_VERIFIED = "subscription_verified"
    ONBOARDING_COMPLETED = "onboarding_completed"
    CATEGORY_VIEWED = "category_viewed"
    OFFER_VIEWED = "offer_viewed"
    REFERRAL_CLICKED = "referral_clicked"
    REGISTRATION = "registration"
    REMINDER_SENT = "reminder_sent"
    FOLLOWUP_30_SENT = "followup_30_sent"
    BROADCAST_RECEIVED = "broadcast_received"
    REENGAGEMENT_SENT = "reengagement_sent"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    user: Mapped[User] = relationship(back_populates="events")
