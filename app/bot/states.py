from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    deal = State()
    competitive_group = State()
    display_data = State()
