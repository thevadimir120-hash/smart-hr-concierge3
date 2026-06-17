"""Backward-compatible re-export."""
from app.database.seed import build_offers, seed_database

__all__ = ["build_offers", "seed_database"]
