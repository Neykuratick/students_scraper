from bot.misc import dp
from aiogram.dispatcher.filters import Command
from aiogram.types import Message


@dp.message_handler(Command('start'))
async def authenticate(message: Message):
    await message.answer(
        'Привет! Я помощник абитуриента ИМО. Сообщи мне свои полные Фамилию Имя Отчество в '
        'именительном падеже (пример Морозова Яна Владимировна), и я помогу оценить твои шансы на '
        'бюджет на текущий момент.'
    )
