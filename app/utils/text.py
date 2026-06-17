from __future__ import annotations

from app.models.offer import Offer

CATEGORY_LABELS: dict[str, str] = {
    "banking": "🏦 Банковские продукты",
    "delivery": "🚚 Доставка и логистика",
    "jobs": "💼 Трудоустройство и вакансии",
    "remote": "💻 Удаленная работа",
    "beginner": "🌱 Подработка для новичков",
}


def format_offer_card(offer: Offer) -> str:
    return (
        f"<b>{offer.title}</b>\n\n"
        f"{offer.short_description}\n\n"
        f"<b>Преимущества:</b>\n{offer.benefits}\n\n"
        f"<b>Доход:</b> {offer.salary_info}"
    )


def format_category_intro(category: str) -> str:
    intros = {
        "banking": "Оформление банковских карт с выгодными условиями и кэшбэком.",
        "delivery": (
            "Актуальные вакансии в доставке и логистике — гибкий график "
            "и быстрый старт без опыта."
        ),
        "jobs": "Официальные вакансии в крупных компаниях — офис, удаленка и разъезд.",
        "remote": "Работа из дома: поддержка, продажи и другие направления.",
        "beginner": "Простые форматы для старта — можно совмещать с учебой.",
    }
    label = CATEGORY_LABELS.get(category, category)
    intro = intros.get(category, "Актуальные предложения в этой категории.")
    return f"{label}\n\n{intro}"
