from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states.lead_form import LeadForm
from bot.keyboards.form_kb import cancel_keyboard
from bot.services.lead_service import create_lead
from bot.database.schemas import LeadCreate
from bot.database.db_helper import db_helper
from bot.utils.validators import validate_phone

router = Router()

@router.message(F.text == "📩 Оставить заявку")
async def start_form(message: Message, state: FSMContext):

    await state.set_state(LeadForm.waiting_for_name)

    await message.answer(
        "Введите ваше имя:",
        reply_markup=cancel_keyboard()
    )

@router.message(LeadForm.waiting_for_name)
async def get_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)

    await state.set_state(LeadForm.waiting_for_phone)

    await message.answer("Введите телефон:")

@router.message(LeadForm.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):

    phone = message.text

    if not validate_phone(phone):
        await message.answer("Введите корректный телефон")
        return

    await state.update_data(phone=phone)

    await state.set_state(LeadForm.waiting_for_email)

    await message.answer("Введите email (или - чтобы пропустить):")

@router.message(LeadForm.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):

    phone = message.text

    if not validate_phone(phone):
        await message.answer("Введите корректный телефон")
        return

    await state.update_data(phone=phone)

    await state.set_state(LeadForm.waiting_for_email)

    await message.answer("Введите email (или - чтобы пропустить):")

@router.message(LeadForm.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):

    phone = message.text

    if not validate_phone(phone):
        await message.answer("Введите корректный телефон")
        return

    await state.update_data(phone=phone)

    await state.set_state(LeadForm.waiting_for_email)

    await message.answer("Введите email (или - чтобы пропустить):")

