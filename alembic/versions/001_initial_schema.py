"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-15

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("desired_income", sa.String(length=64), nullable=True),
        sa.Column("work_format", sa.String(length=64), nullable=True),
        sa.Column("is_subscribed_verified", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("last_active_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_id"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])

    op.create_table(
        "offers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("short_description", sa.Text(), nullable=False),
        sa.Column("benefits", sa.Text(), nullable=False),
        sa.Column("salary_info", sa.String(length=255), nullable=False),
        sa.Column("bonuses", sa.String(length=512), nullable=False),
        sa.Column("image_path", sa.String(length=512), nullable=True),
        sa.Column("referral_link", sa.String(length=1024), nullable=False),
        sa.Column("payout", sa.String(length=128), nullable=False),
        sa.Column("cta_text", sa.String(length=128), nullable=False, server_default="Подать заявку"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_offers_category", "offers", ["category"])
    op.create_index("ix_offers_is_active", "offers", ["is_active"])

    op.create_table(
        "clicks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=False),
        sa.Column("clicked_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["offer_id"], ["offers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_clicks_user_id", "clicks", ["user_id"])
    op.create_index("ix_clicks_offer_id", "clicks", ["offer_id"])
    op.create_index("ix_clicks_clicked_at", "clicks", ["clicked_at"])

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.Text(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_events_user_id", "events", ["user_id"])
    op.create_index("ix_events_event_type", "events", ["event_type"])
    op.create_index("ix_events_timestamp", "events", ["timestamp"])

    op.create_table(
        "offer_views",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=False),
        sa.Column("viewed_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("reminder_sent", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("clicked", sa.Boolean(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["offer_id"], ["offers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_offer_views_user_id", "offer_views", ["user_id"])
    op.create_index("ix_offer_views_offer_id", "offer_views", ["offer_id"])
    op.create_index("ix_offer_views_viewed_at", "offer_views", ["viewed_at"])

    op.create_table(
        "bot_settings",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("bot_settings")
    op.drop_table("offer_views")
    op.drop_table("events")
    op.drop_table("clicks")
    op.drop_table("offers")
    op.drop_table("users")
