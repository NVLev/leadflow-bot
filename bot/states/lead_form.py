from aiogram.fsm.state import State, StatesGroup


class LeadForm(StatesGroup):
    waiting_for_service = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_message = State()
