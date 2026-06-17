from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models.offer import Offer
from app.utils.text import CATEGORY_LABELS


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📂 Каталог вакансий", callback_data="menu_catalog")],
            [InlineKeyboardButton(text="🎯 Подбор под мой профиль", callback_data="menu_matched")],
            [InlineKeyboardButton(text="ℹ️ Как это работает", callback_data="menu_how")],
        ],
    )


def categories_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"cat_{key}")]
        for key, label in CATEGORY_LABELS.items()
    ]
    rows.append([InlineKeyboardButton(text="◀️ В меню", callback_data="back_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def offers_list_keyboard(offers: list[Offer], category: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=offer.title, callback_data=f"offer_{offer.id}")]
        for offer in offers
    ]
    rows.append([InlineKeyboardButton(text="◀️ К категориям", callback_data="menu_catalog")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _cta_label(offer: Offer) -> str:
    if offer.cta_text in ("🚀 Занять рабочее место", "📝 Заполнить анкету"):
        return offer.cta_text
    if offer.category == "banking" or "карт" in offer.title.lower():
        return "📝 Заполнить анкету"
    return "🚀 Занять рабочее место"


def offer_card_keyboard(offer: Offer) -> InlineKeyboardMarkup:
    if offer.is_paused:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📂 Смотреть доставку", callback_data="cat_delivery")],
                [InlineKeyboardButton(text="💻 Смотреть удаленку", callback_data="cat_remote")],
                [InlineKeyboardButton(text="◀️ Назад", callback_data=f"cat_{offer.category}")],
            ],
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_cta_label(offer), url=offer.referral_link)],
            [InlineKeyboardButton(text="◀️ Назад к списку", callback_data=f"cat_{offer.category}")],
            [InlineKeyboardButton(text="🏠 В меню", callback_data="back_menu")],
        ],
    )
