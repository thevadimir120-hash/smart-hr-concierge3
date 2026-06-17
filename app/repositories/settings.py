from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bot_settings import BotSetting

DEFAULT_WELCOME = (
    "Привет! Я бот Workora. 🚀 Помогаю быстро находить честную подработку и работу "
    "прямо в твоем городе.\n"
    "Здесь собраны только лучшие вакансии с гибким графиком, хорошей оплатой и без "
    "требований к опыту.\n"
    "Чтобы открыть каталог доступных мест, подпишись на наш официальный канал — туда мы "
    "выкладываем новые вакансии и отчеты по заработкам ребят."
)

DEFAULT_REMINDER = (
    "⚡ Места по этой вакансии в твоем районе почти разобрали. "
    "Успей откликнуться, пока слоты еще открыты."
)

DEFAULT_FOLLOWUP_30 = (
    "Слушай, проверил базу — места по этой вакансии в твоем районе почти разобрали. ⏳ "
    "Ты успел отправить анкету на сайте? Если ссылка зависла, просто нажми на кнопку "
    "выше еще раз. Если передумал, напиши /menu, подберем что-то другое."
)


class SettingsRepository:
    WELCOME_KEY = "welcome_text"
    REMINDER_KEY = "reminder_text"
    FOLLOWUP_30_KEY = "followup_30_text"

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, key: str, default: str = "") -> str:
        result = await self._session.execute(
            select(BotSetting).where(BotSetting.key == key),
        )
        row = result.scalar_one_or_none()
        return row.value if row else default

    async def set(self, key: str, value: str) -> None:
        result = await self._session.execute(
            select(BotSetting).where(BotSetting.key == key),
        )
        row = result.scalar_one_or_none()
        if row:
            row.value = value
        else:
            self._session.add(BotSetting(key=key, value=value))
        await self._session.flush()

    async def get_welcome_text(self) -> str:
        return await self.get(self.WELCOME_KEY, DEFAULT_WELCOME)

    async def get_reminder_text(self) -> str:
        return await self.get(self.REMINDER_KEY, DEFAULT_REMINDER)

    async def get_followup_30_text(self) -> str:
        return await self.get(self.FOLLOWUP_30_KEY, DEFAULT_FOLLOWUP_30)

    async def ensure_defaults(self) -> None:
        if not await self.get(self.WELCOME_KEY):
            await self.set(self.WELCOME_KEY, DEFAULT_WELCOME)
        if not await self.get(self.REMINDER_KEY):
            await self.set(self.REMINDER_KEY, DEFAULT_REMINDER)
        if not await self.get(self.FOLLOWUP_30_KEY):
            await self.set(self.FOLLOWUP_30_KEY, DEFAULT_FOLLOWUP_30)
