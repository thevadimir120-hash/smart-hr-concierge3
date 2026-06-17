from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    broadcast_message = State()
    edit_welcome = State()
    edit_referral_offer_id = State()
    edit_referral_link = State()
    add_offer_title = State()
    add_offer_category = State()
    add_offer_description = State()
    add_offer_benefits = State()
    add_offer_salary = State()
    add_offer_bonuses = State()
    add_offer_payout = State()
    add_offer_link = State()
