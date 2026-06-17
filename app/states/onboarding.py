from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    city = State()
    time_commitment = State()
