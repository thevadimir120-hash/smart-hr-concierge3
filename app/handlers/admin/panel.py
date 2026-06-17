from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.admin import (
    admin_main_keyboard,
    admin_offer_actions_keyboard,
    admin_offers_keyboard,
)
from app.models.offer import Offer
from app.services.admin import AdminService
from app.services.broadcast import BroadcastService
from app.states import AdminStates

router = Router(name="admin_panel")


@router.message(Command("admin"))
async def admin_entry(message: Message) -> None:
    await message.answer(
        "<b>🛠 Админ-панель Workora</b>\n\nВыбери действие:",
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(F.data == "adm_back")
async def admin_back(callback: CallbackQuery) -> None:
    if not callback.message:
        return
    await callback.answer()
    await callback.message.edit_text(
        "<b>🛠 Панель администратора</b>",
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(F.data == "adm_daily")
async def admin_daily(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.message:
        return
    service = AdminService(session)
    stats = await service.analytics.daily_stats()
    await callback.answer()
    await callback.message.edit_text(
        service.analytics.format_daily(stats),
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(F.data == "adm_full")
async def admin_full(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.message:
        return
    service = AdminService(session)
    stats = await service.analytics.full_stats()
    await callback.answer()
    await callback.message.edit_text(
        service.analytics.format_full(stats),
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(F.data == "adm_welcome")
async def admin_welcome_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(AdminStates.edit_welcome)
    if callback.message:
        await callback.message.answer(
            "Отправьте новый welcome-текст (HTML поддерживается):",
        )


@router.message(AdminStates.edit_welcome)
async def admin_welcome_save(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text:
        await message.answer("Отправьте текст сообщением.")
        return
    await AdminService(session).set_welcome_text(message.text)
    await state.clear()
    await message.answer("Welcome-текст обновлён ✅", reply_markup=admin_main_keyboard())


@router.callback_query(F.data == "adm_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(AdminStates.broadcast_message)
    if callback.message:
        await callback.message.answer(
            "Отправьте текст рассылки (HTML). Будет отправлено всем пользователям с завершённым onboarding.",
        )


@router.message(AdminStates.broadcast_message)
async def admin_broadcast_send(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if not message.text or not message.bot:
        await message.answer("Отправьте текст.")
        return
    broadcast = BroadcastService(session, message.bot)
    success, failed = await broadcast.send_to_all(message.text)
    await state.clear()
    await message.answer(
        f"Рассылка завершена.\nУспешно: {success}\nОшибок: {failed}",
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(F.data == "adm_offers")
async def admin_offers_list(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.message:
        return
    offers = await AdminService(session).list_offers()
    await callback.answer()
    await callback.message.edit_text(
        "<b>Управление офферами</b>\n\nВыберите оффер:",
        reply_markup=admin_offers_keyboard(offers),
    )


@router.callback_query(F.data.startswith("adm_offer_"))
async def admin_offer_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.data or not callback.message:
        return
    offer_id = int(callback.data.removeprefix("adm_offer_"))
    offers = await AdminService(session).list_offers()
    offer = next((o for o in offers if o.id == offer_id), None)
    if not offer:
        await callback.answer("Оффер не найден", show_alert=True)
        return
    await callback.answer()
    status = "активен" if offer.is_active else "отключён"
    await callback.message.edit_text(
        f"<b>{offer.title}</b> ({status})\n\n"
        f"Категория: {offer.category}\n"
        f"Ссылка: {offer.referral_link}\n"
        f"Внутр. метрика: {offer.payout or '—'}",
        reply_markup=admin_offer_actions_keyboard(offer.id, offer.is_active),
    )


@router.callback_query(F.data.startswith("adm_toggle_"))
async def admin_toggle_offer(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.data or not callback.message:
        return
    offer_id = int(callback.data.removeprefix("adm_toggle_"))
    offer = await AdminService(session).toggle_offer(offer_id)
    if not offer:
        await callback.answer("Оффер не найден", show_alert=True)
        return
    status = "включён" if offer.is_active else "отключён"
    await callback.answer(f"Оффер {status}")
    await callback.message.edit_reply_markup(
        reply_markup=admin_offer_actions_keyboard(offer.id, offer.is_active),
    )


@router.callback_query(F.data.startswith("adm_edit_link_"))
async def admin_edit_link_start(
    callback: CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.data:
        return
    offer_id = int(callback.data.removeprefix("adm_edit_link_"))
    await state.set_state(AdminStates.edit_referral_link)
    await state.update_data(offer_id=offer_id)
    await callback.answer()
    if callback.message:
        await callback.message.answer("Отправьте новую реферальную ссылку:")


@router.message(AdminStates.edit_referral_link)
async def admin_edit_link_save(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
) -> None:
    if not message.text:
        await message.answer("Отправьте ссылку текстом.")
        return
    data = await state.get_data()
    offer_id = int(data["offer_id"])
    offer = await AdminService(session).update_referral_link(offer_id, message.text)
    await state.clear()
    if not offer:
        await message.answer("Оффер не найден.")
        return
    await message.answer(
        f"Ссылка для «{offer.title}» обновлена ✅",
        reply_markup=admin_main_keyboard(),
    )


@router.callback_query(F.data == "adm_add_offer")
async def admin_add_offer_start(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(AdminStates.add_offer_title)
    if callback.message:
        await callback.message.answer("Название нового оффера:")


@router.message(AdminStates.add_offer_title)
async def add_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await state.set_state(AdminStates.add_offer_category)
    await message.answer(
        "Категория: banking / delivery / jobs / remote / beginner",
    )


@router.message(AdminStates.add_offer_category)
async def add_category(message: Message, state: FSMContext) -> None:
    await state.update_data(category=(message.text or "").strip().lower())
    await state.set_state(AdminStates.add_offer_description)
    await message.answer("Краткое описание:")


@router.message(AdminStates.add_offer_description)
async def add_description(message: Message, state: FSMContext) -> None:
    await state.update_data(short_description=message.text)
    await state.set_state(AdminStates.add_offer_benefits)
    await message.answer("Преимущества (можно списком):")


@router.message(AdminStates.add_offer_benefits)
async def add_benefits(message: Message, state: FSMContext) -> None:
    await state.update_data(benefits=message.text)
    await state.set_state(AdminStates.add_offer_salary)
    await message.answer("Информация о доходе:")


@router.message(AdminStates.add_offer_salary)
async def add_salary(message: Message, state: FSMContext) -> None:
    await state.update_data(salary_info=message.text)
    await state.set_state(AdminStates.add_offer_bonuses)
    await message.answer("Бонусы:")


@router.message(AdminStates.add_offer_bonuses)
async def add_bonuses(message: Message, state: FSMContext) -> None:
    await state.update_data(bonuses=message.text)
    await state.set_state(AdminStates.add_offer_payout)
    await message.answer("Внутр. метрика (число, только для админки):")


@router.message(AdminStates.add_offer_payout)
async def add_payout(message: Message, state: FSMContext) -> None:
    try:
        payout_val = float((message.text or "0").replace(",", "."))
    except ValueError:
        payout_val = 0.0
    await state.update_data(payout=payout_val)
    await state.set_state(AdminStates.add_offer_link)
    await message.answer("Реферальная ссылка:")


@router.message(AdminStates.add_offer_link)
async def add_link(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    offer = Offer(
        title=data["title"],
        category=data["category"],
        short_description=data["short_description"],
        benefits=data["benefits"],
        salary_info=data["salary_info"],
        bonuses=data["bonuses"],
        payout=data["payout"],
        referral_link=message.text or "",
    )
    created = await AdminService(session).create_offer(offer)
    await state.clear()
    await message.answer(
        f"Оффер «{created.title}» создан (id={created.id}) ✅",
        reply_markup=admin_main_keyboard(),
    )
