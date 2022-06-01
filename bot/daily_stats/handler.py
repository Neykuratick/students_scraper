from aiogram.types import Message
from datetime import datetime, timedelta
from aiogram.dispatcher.router import Router
from database.deals_crud import db

daily_stats_router = Router()


@daily_stats_router.message(commands=['stats'])
async def get(message: Message):
    requesting_timestamp = datetime.now() - timedelta(days=1)

    deals = []
    async for deal in db.get(modified_date=requesting_timestamp):
        deals.append(deal)

    await message.answer(str(len(deals)))
