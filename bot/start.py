from aiogram.types import Message
from bot.states import Form
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.router import Router

auth_router = Router()


@auth_router.message(commands=['start'])
async def authenticate(message: Message, state: FSMContext):
    await state.set_state(Form.deal)

    await message.answer(
        '👋 Привет! Я помощник абитуриента ИМО. Сообщи мне свои полные Фамилию Имя Отчество в '
        'именительном падеже (пример Морозова Яна Владимировна), и я помогу оценить твои шансы на '
        'бюджет на текущий момент'
    )


"""
TODO
---
Реализовать выбор абитуриента
Реализовать выбор направления
"""
