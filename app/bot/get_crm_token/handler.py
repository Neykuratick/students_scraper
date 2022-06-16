from aiogram.dispatcher.router import Router
from aiogram.types import Message

get_crm_token_router = Router()


@get_crm_token_router.message(commands=['token'])
async def get(message: Message):
    with open('test.txt', 'r') as f:
        refresh_token = f.read()
        
    await message.answer(refresh_token)
