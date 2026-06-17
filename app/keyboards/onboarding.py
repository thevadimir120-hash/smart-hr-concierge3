from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TIME_COMMITMENT_OPTIONS = [
    ("⏱ Пару часов в день", "time_few_hours"),
    ("💼 Полный день", "time_full_day"),
    ("🏠 Удаленка (с телефона)", "time_remote"),
    ("🔄 Только выходные", "time_weekends"),
]


def time_commitment_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=label, callback_data=code)]
        for label, code in TIME_COMMITMENT_OPTIONS
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


TIME_COMMITMENT_MAP = {code: label for label, code in TIME_COMMITMENT_OPTIONS}
