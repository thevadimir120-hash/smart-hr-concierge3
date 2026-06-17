from __future__ import annotations

import os
from functools import lru_cache
from typing import FrozenSet

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.paths import DEFAULT_AMVERA_DB_URL, get_database_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(..., alias="BOT_TOKEN")
    admin_ids: FrozenSet[int] = Field(default_factory=frozenset, alias="ADMIN_IDS")
    channel_id: str = Field(default="@Workora_student", alias="CHANNEL_ID")
    channel_url: str = Field(
        default="https://t.me/Workora_student",
        alias="CHANNEL_URL",
    )
    database_url: str = Field(
        default=DEFAULT_AMVERA_DB_URL,
        alias="DATABASE_URL",
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    reminder_hours: int = Field(default=2, alias="REMINDER_HOURS")
    followup_minutes: int = Field(default=30, alias="FOLLOWUP_MINUTES")
    weekly_broadcast_cron: str = Field(default="0 10 * * 1", alias="WEEKLY_BROADCAST_CRON")
    bonus_notification_cron: str = Field(default="0 12 * * 3", alias="BONUS_NOTIFICATION_CRON")
    payout_notification_cron: str = Field(
        default="0 11 * * 5",
        alias="PAYOUT_NOTIFICATION_CRON",
    )
    reengagement_days: int = Field(default=7, alias="REENGAGEMENT_DAYS")
    flood_rate_limit: float = Field(default=0.5, alias="FLOOD_RATE_LIMIT")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: object) -> FrozenSet[int]:
        if value is None or value == "":
            return frozenset()
        if isinstance(value, (set, frozenset)):
            return frozenset(int(item) for item in value)
        raw = str(value).strip()
        if not raw:
            return frozenset()
        return frozenset(int(part.strip()) for part in raw.split(",") if part.strip())


@lru_cache
def get_settings() -> Settings:
    # BOT_TOKEN и DATABASE_URL читаются из os.environ (Amvera / .env)
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
