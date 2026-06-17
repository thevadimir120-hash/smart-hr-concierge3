"""Проверка проекта Workora перед загрузкой на хостинг."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REQUIRED_IMAGES = [
    "assets/yandex_delivery.jpg",
    "assets/samokat_delivery.jpg",
    "assets/kuper_picker.jpg",
    "assets/kuper_courier.jpg",
    "assets/tbank_career.jpg",
    "assets/alfa_delivery_job.jpg",
    "assets/mts_support.jpg",
    "assets/mts_sales.jpg",
    "assets/tbank_platinum.jpg",
    "assets/gpb_smart.jpg",
    "assets/alfa_youth.jpg",
    "assets/gpb_115.jpg",
    "assets/vtb_debit.jpg",
    "assets/beginner_mystery.jpg",
    "assets/beginner_promo.jpg",
]

REQUIRED_FILES = [
    "main.py",
    "requirements.txt",
    "Dockerfile",
    "app/database/seed.py",
    "app/handlers/start.py",
    "app/handlers/onboarding.py",
    "app/handlers/offers.py",
]

FORBIDDEN_UPLOAD = [".env", "data/workora.db", "data/smart_hr.db", "__pycache__"]


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            errors.append(f"Нет файла: {rel}")

    for rel in REQUIRED_IMAGES:
        p = ROOT / rel
        if not p.exists():
            # допускаем .png
            alt = p.with_suffix(".png")
            if alt.exists():
                warnings.append(f"Найден {alt.name}, в seed указан {p.name} — переименуй или обнови seed.py")
            else:
                errors.append(f"Нет фото: {rel}")

    assets_dir = ROOT / "assets"
    if assets_dir.exists():
        extra = [
            f.name
            for f in assets_dir.iterdir()
            if f.is_file() and f.name not in {Path(x).name for x in REQUIRED_IMAGES}
        ]
        if extra:
            warnings.append(f"Лишние файлы в assets/ (не страшно): {', '.join(extra[:10])}")

    if (ROOT / ".env").exists():
        warnings.append("Файл .env есть локально — НЕ загружай его на GitHub/Bothost (только переменные в панели)")

    try:
        from app.database.seed import build_offers

        offers = build_offers()
        if len(offers) != 15:
            errors.append(f"В seed должно быть 15 офферов, сейчас: {len(offers)}")
        for o in offers:
            if not o.referral_link.startswith("http"):
                errors.append(f"Некорректная ссылка у: {o.title}")
    except Exception as exc:
        errors.append(f"Ошибка импорта seed: {exc}")

    print("=== Проверка Workora ===\n")
    if errors:
        print("ОШИБКИ:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("Критических ошибок нет.")

    if warnings:
        print("\nПРЕДУПРЕЖДЕНИЯ:")
        for w in warnings:
            print(f"  - {w}")

    print(f"\nПапка проекта:\n  {ROOT}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
