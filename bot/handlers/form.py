import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.db_helper import db_helper
from bot.database.schemas import LeadCreate
from bot.integrations.google_sheets import google_sheets
from bot.keyboards.form_kb import cancel_keyboard, service_keyboard
from bot.keyboards.menu import main_menu
from bot.services.lead_service import create_lead
from bot.services.notify_service import notify_admins
from bot.states.lead_form import LeadForm
from bot.utils.validators import validate_phone

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "📩 Оставить заявку")
async def start_form(message: Message, state: FSMContext):
    logger.info("User %s started lead form", message.from_user.id)

    await state.set_state(LeadForm.waiting_for_service)

    await message.answer(
        "Выберите, что вас интересует:",
        reply_markup=service_keyboard(),
    )


@router.callback_query(LeadForm.waiting_for_service, F.data.startswith("service:"))
async def get_service(callback: CallbackQuery, state: FSMContext) -> None:
    service = callback.data.split(":", 1)[1]
    logger.info("Service selected: %s", service)

    await state.update_data(service=service)
    await state.set_state(LeadForm.waiting_for_name)

    await callback.message.edit_text(f"Вы выбрали: <b>{service}</b>", parse_mode="HTML")
    await callback.message.answer("Введите ваше имя:", reply_markup=cancel_keyboard())
    await callback.answer()


@router.message(LeadForm.waiting_for_name)
async def get_name(message: Message, state: FSMContext) -> None:
    logger.info("Name received: %s", message.text)
    await state.update_data(name=message.text)
    await state.set_state(LeadForm.waiting_for_phone)
    await message.answer("Введите номер телефона:")


@router.message(LeadForm.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext) -> None:
    phone = message.text
    logger.info("Phone received: %s", phone)

    if not validate_phone(phone):
        await message.answer(
            "Введите корректный номер телефона (например, +79991234567):"
        )
        return

    await state.update_data(phone=phone)
    await state.set_state(LeadForm.waiting_for_email)
    await message.answer("Введите email (или — чтобы пропустить):")


@router.message(LeadForm.waiting_for_email)
async def get_email(message: Message, state: FSMContext) -> None:
    email = message.text
    logger.info("Email received: %s", email)

    if email == "-":
        email = None

    await state.update_data(email=email)
    await state.set_state(LeadForm.waiting_for_message)
    await message.answer("Удобное время для связи или пожелания:")


@router.message(LeadForm.waiting_for_message)
async def get_message(message: Message, state: FSMContext) -> None:
    logger.info("Message received: %s", message.text)
    await state.update_data(message=message.text)

    data = await state.get_data()
    logger.info("FSM data: %s", data)

    try:
        lead_data = LeadCreate(
            user_id=message.from_user.id,
            name=data["name"],
            phone=data["phone"],
            email=data.get("email"),
            service=data.get("service"),
            message=data["message"],
        )

        async for session in db_helper.session_getter():
            lead = await create_lead(session, lead_data)

        await notify_admins(message.bot, lead)
        await asyncio.to_thread(google_sheets.append_lead, lead)

    except Exception:
        logger.exception("Error creating lead")
        await message.answer(
            "⚠️ Произошла ошибка. Попробуйте ещё раз.",
            reply_markup=main_menu(),
        )
        await state.clear()
        return

    await message.answer(
        "✅ Спасибо! Мы получили вашу заявку и свяжемся с вами в ближайшее время.",
        reply_markup=main_menu(),
    )
    await state.clear()
