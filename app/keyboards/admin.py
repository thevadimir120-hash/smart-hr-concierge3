from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models.offer import Offer


def admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика за сегодня", callback_data="adm_daily")],
            [InlineKeyboardButton(text="📈 Общая аналитика", callback_data="adm_full")],
            [InlineKeyboardButton(text="📣 Рассылка", callback_data="adm_broadcast")],
            [InlineKeyboardButton(text="✏️ Welcome-текст", callback_data="adm_welcome")],
            [InlineKeyboardButton(text="🔗 Офферы и ссылки", callback_data="adm_offers")],
            [InlineKeyboardButton(text="➕ Добавить оффер", callback_data="adm_add_offer")],
        ],
    )


def admin_offers_keyboard(offers: list[Offer]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for offer in offers:
        status = "✅" if offer.is_active else "⛔"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{status} {offer.title[:40]}",
                    callback_data=f"adm_offer_{offer.id}",
                ),
            ],
        )
    rows.append([InlineKeyboardButton(text="◀️ Назад", callback_data="adm_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_offer_actions_keyboard(offer_id: int, is_active: bool) -> InlineKeyboardMarkup:
    toggle_text = "⛔ Отключить" if is_active else "✅ Включить"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 Изменить ссылку",
                    callback_data=f"adm_edit_link_{offer_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=toggle_text,
                    callback_data=f"adm_toggle_{offer_id}",
                ),
            ],
            [InlineKeyboardButton(text="◀️ К списку", callback_data="adm_offers")],
        ],
    )
