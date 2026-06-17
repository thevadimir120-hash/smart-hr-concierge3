from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.keyboards import main_menu_keyboard, subscription_keyboard
from app.repositories.settings import SettingsRepository
from app.services.subscription import SubscriptionService
from app.services.user import UserService
from app.states import OnboardingStates

router = Router(name="start")
settings = get_settings()

SUBSCRIBE_EXTRA = (
    "Чтобы открыть каталог доступных мест, подпишись на наш официальный канал — "
    "туда мы выкладываем новые вакансии и отчеты по заработкам ребят."
)


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession, state: FSMContext) -> None:
    if not message.from_user:
        return
    await state.clear()
    user_service = UserService(session)
    settings_repo = SettingsRepository(session)
    user, _ = await user_service.register_start(
        message.from_user.id,
        message.from_user.username,
    )
    welcome = await settings_repo.get_welcome_text()

    if not user.is_subscribed_verified:
        sub_service = SubscriptionService(message.bot, settings)
        if await sub_service.is_subscribed(message.from_user.id):
            user = await user_service.mark_subscribed(user)
        else:
            await message.answer(
                welcome,
                reply_markup=subscription_keyboard(settings.channel_url),
            )
            return

    await _route_after_subscription(message, user.onboarding_completed, welcome, state)


@router.callback_query(F.data == "check_subscription")
async def check_subscription(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    if not callback.from_user or not callback.message:
        return
    sub_service = SubscriptionService(callback.bot, settings)
    user_service = UserService(session)
    settings_repo = SettingsRepository(session)

    if not await sub_service.is_subscribed(callback.from_user.id):
        await callback.answer(
            "Подписка пока не найдена. Подпишись на канал и нажми кнопку снова.",
            show_alert=True,
        )
        return

    user, _ = await user_service.register_start(
        callback.from_user.id,
        callback.from_user.username,
    )
    user = await user_service.mark_subscribed(user)
    welcome = await settings_repo.get_welcome_text()
    await callback.answer("Подписка подтверждена ✅", show_alert=True)
    await _route_after_subscription(
        callback.message,
        user.onboarding_completed,
        welcome,
        state,
        edit=True,
    )


async def _route_after_subscription(
    message: Message,
    onboarding_completed: bool,
    welcome: str,
    state: FSMContext,
    *,
    edit: bool = False,
) -> None:
    if not onboarding_completed:
        text = (
            f"{welcome}\n\n"
            "Отлично! Уточню пару деталей, чтобы показать подходящие вакансии.\n\n"
            "В каком городе ты ищешь подработку?"
        )
        await state.set_state(OnboardingStates.city)
        if edit:
            await message.edit_text(text)
        else:
            await message.answer(text)
        return

    text = "Открываю каталог актуальных позиций под твой профиль 👇"
    if edit:
        await message.edit_text(text, reply_markup=main_menu_keyboard())
    else:
        await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(Command("menu"))
async def cmd_menu(message: Message, session: AsyncSession) -> None:
    if not message.from_user:
        return
    user_service = UserService(session)
    await user_service.touch(message.from_user.id)
    await message.answer(
        "Главное меню Workora:",
        reply_markup=main_menu_keyboard(),
    )
