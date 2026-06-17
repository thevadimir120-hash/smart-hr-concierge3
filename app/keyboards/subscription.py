from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def subscription_keyboard(channel_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Подписаться на канал", url=channel_url)],
            [
                InlineKeyboardButton(
                    text="✅ Я подписался — проверить",
                    callback_data="check_subscription",
                ),
            ],
        ],
    )
