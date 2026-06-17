from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.paths import get_assets_dir
from app.keyboards import (
    categories_keyboard,
    main_menu_keyboard,
    offer_card_keyboard,
    offers_list_keyboard,
)
from app.models.offer import OfferCategory
from app.repositories.user import UserRepository
from app.services.offer import OfferService
from app.services.user import UserService
from app.utils.text import CATEGORY_LABELS, format_category_intro

router = Router(name="offers")
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "back_menu")
async def back_menu(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.from_user or not callback.message:
        return
    await UserService(session).touch(callback.from_user.id)
    await callback.answer()
    await callback.message.edit_text(
        "Главное меню Workora:",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data == "menu_catalog")
async def show_catalog(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.message:
        return
    await callback.answer()
    await callback.message.edit_text(
        "Выбери категорию — покажу проверенные вакансии:",
        reply_markup=categories_keyboard(),
    )


@router.callback_query(F.data == "menu_how")
async def how_it_works(callback: CallbackQuery) -> None:
    if not callback.message:
        return
    await callback.answer()
    await callback.message.edit_text(
        "<b>Как работает Workora</b>\n\n"
        "1️⃣ Ты отвечаешь на пару вопросов (город и график).\n"
        "2️⃣ Мы показываем категории вакансий с реальными условиями.\n"
        "3️⃣ Ты выбираешь подходящую позицию и переходишь на официальную анкету.\n\n"
        "Без пустых обещаний — только проверенные предложения с понятной оплатой.",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(F.data == "menu_matched")
async def show_matched(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.from_user or not callback.message:
        return
    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    if not user or not user.onboarding_completed:
        await callback.answer("Сначала заверши анкету через /start", show_alert=True)
        return

    category = _match_category(user.work_format or "")
    offer_service = OfferService(session)
    offers = await offer_service.list_active_by_category(category)
    if not offers:
        await callback.answer("В этой категории пока нет вакансий", show_alert=True)
        return
    await callback.answer()
    label = CATEGORY_LABELS.get(category, category)
    await callback.message.edit_text(
        f"<b>Подборка для тебя</b>\n{label}\n\n"
        "Позиции подобраны под твой график:",
        reply_markup=offers_list_keyboard(offers, category),
    )


@router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.from_user or not callback.data or not callback.message:
        return
    category = callback.data.removeprefix("cat_")
    offer_service = OfferService(session)
    await offer_service.track_category_view(callback.from_user.id, category)
    offers = await offer_service.list_active_by_category(category)
    await callback.answer()
    if not offers:
        await callback.message.edit_text(
            "В этой категории сейчас нет открытых вакансий.",
            reply_markup=categories_keyboard(),
        )
        return
    await callback.message.edit_text(
        format_category_intro(category),
        reply_markup=offers_list_keyboard(offers, category),
    )


async def _send_offer_card(
    callback: CallbackQuery,
    offer_service: OfferService,
    offer_id: int,
    telegram_id: int,
) -> None:
    if not callback.message:
        return
    offer, text = await offer_service.open_offer(telegram_id, offer_id)
    if not offer or not text:
        await callback.answer("Вакансия недоступна", show_alert=True)
        return

    keyboard = offer_card_keyboard(offer)
    image_path = offer_service.resolve_image(offer, get_assets_dir())

    if image_path:
        try:
            await callback.message.delete()
            await callback.message.answer_photo(
                photo=FSInputFile(image_path),
                caption=text,
                reply_markup=keyboard,
            )
            return
        except TelegramAPIError as exc:
            logger.warning("Photo send failed for offer %s: %s", offer_id, exc)

    try:
        await callback.message.edit_text(text, reply_markup=keyboard)
    except TelegramAPIError:
        await callback.message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("offer_"))
async def show_offer(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.from_user or not callback.data:
        return
    offer_id = int(callback.data.removeprefix("offer_"))
    await callback.answer()
    await _send_offer_card(
        callback,
        OfferService(session),
        offer_id,
        callback.from_user.id,
    )


@router.callback_query(F.data.startswith("go_"))
async def track_intent_click(callback: CallbackQuery, session: AsyncSession) -> None:
    if not callback.from_user or not callback.data:
        return
    offer_id = int(callback.data.removeprefix("go_"))
    await OfferService(session).track_referral_click(callback.from_user.id, offer_id)
    await callback.answer("Переход засчитан ✅")


def _match_category(work_format: str) -> str:
    lowered = work_format.lower()
    if "удал" in lowered or "телефон" in lowered:
        return OfferCategory.REMOTE
    if "выходн" in lowered:
        return OfferCategory.BEGINNER
    if "полный" in lowered:
        return OfferCategory.JOBS
    if "час" in lowered:
        return OfferCategory.DELIVERY
    return OfferCategory.DELIVERY
