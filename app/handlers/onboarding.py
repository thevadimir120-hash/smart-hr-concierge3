from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards import TIME_COMMITMENT_MAP, main_menu_keyboard, time_commitment_keyboard
from app.repositories.user import UserRepository
from app.services.user import UserService
from app.states import OnboardingStates

router = Router(name="onboarding")


@router.message(OnboardingStates.city)
async def process_city(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Напиши город текстом, например: Казань")
        return
    await state.update_data(city=message.text.strip())
    await state.set_state(OnboardingStates.time_commitment)
    await message.answer(
        "Сколько времени готов уделять работе?",
        reply_markup=time_commitment_keyboard(),
    )


@router.callback_query(OnboardingStates.time_commitment, F.data.startswith("time_"))
async def process_time_commitment(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if not callback.from_user or not callback.data or not callback.message:
        return
    time_label = TIME_COMMITMENT_MAP.get(callback.data, callback.data)
    data = await state.get_data()
    city = data.get("city", "")

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Сначала нажми /start", show_alert=True)
        return

    user_service = UserService(session)
    await user_service.complete_onboarding(user, city, time_label)
    await state.clear()
    await callback.answer("Профиль сохранен ✅", show_alert=True)
    await callback.message.edit_text(
        "Профиль сохранен ✅ Открываю каталог актуальных позиций...",
        reply_markup=main_menu_keyboard(),
    )
