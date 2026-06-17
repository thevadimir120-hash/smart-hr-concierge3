"""Validate .env before starting the bot locally."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"

PLACEHOLDERS = {
    "BOT_TOKEN": {"your_telegram_bot_token", ""},
    "ADMIN_IDS": {"123456789", ""},
    "CHANNEL_ID": {"@your_hr_channel", ""},
    "CHANNEL_URL": {"https://t.me/your_hr_channel", ""},
}


def load_env() -> dict[str, str]:
    if not ENV_PATH.exists():
        print(f"Missing {ENV_PATH}. Copy .env.example to .env and fill values.")
        sys.exit(1)
    values: dict[str, str] = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip()
    return values


def main() -> None:
    env = load_env()
    errors: list[str] = []

    for key in ("BOT_TOKEN", "ADMIN_IDS", "CHANNEL_ID", "CHANNEL_URL"):
        val = env.get(key, "")
        if not val or val in PLACEHOLDERS.get(key, set()):
            errors.append(f"  - {key} is not configured")

    if errors:
        print("Fix .env before starting:\n" + "\n".join(errors))
        sys.exit(1)

    try:
        from app.config import get_settings

        get_settings.cache_clear()
        settings = get_settings()
    except Exception as exc:
        print(f"Settings error: {exc}")
        sys.exit(1)

    print("Environment OK")
    print(f"  Admins: {sorted(settings.admin_ids)}")
    print(f"  Channel: {settings.channel_id}")
    print(f"  DB: {settings.database_url}")


if __name__ == "__main__":
    main()
