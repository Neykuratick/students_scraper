from aiogram.types import Message

from app.bot.get_statistic.handler import process_name
from app.bot.states import Form
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.router import Router

auth_router = Router()


@auth_router.message(commands=['start'])
async def authenticate(message: Message, state: FSMContext):
    await state.set_state(Form.deal)

    await message.answer(
        '👋 Привет! Я помощник абитуриента ИМО. \n\nЧтобы я смог оценить твои шансы на бюджет на текущий момент, '
        'сообщи мне свою фамилию. Можно ещё имя и отчество, но не обязательно '
        '\n\n✅ Например, что-то одно из этого: \n\n👉Морозова\n👉Морозова Яна\n👉Морозова Яна Владимировна'
    )


@auth_router.message(state='*')
async def launch_statistics(message: Message, state: FSMContext):
    await state.set_state(Form.deal)
    await process_name(message=message, state=state)
