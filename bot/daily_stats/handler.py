from aiogram.types import Message
from datetime import datetime, timedelta
from aiogram.dispatcher.router import Router
from database.deals_crud import db

daily_stats_router = Router()


@daily_stats_router.message(commands=['stats'])
async def get(message: Message):
    stats = {}

    async for deal in db.get():
        try:
            count = stats.get(deal.contact.competitive_group).get('total')
        except:
            stats[deal.contact.competitive_group] = {'total': 0}
            count = 0

        stats[deal.contact.competitive_group] = {'total': count + 1}

    async for deal in db.get(inserted_date=datetime.today() - timedelta(days=1)):  # TODO remove timedelta in prod
        count = stats.get(deal.contact.competitive_group).get('today') or 0
        stats[deal.contact.competitive_group]['today'] = count + 1

    text = "📈 Всего заявок:\n\n"
    for key, item in stats.items():
        text += f"{key}: {item['total']}\n"

    text += "\n📆 Заявок за сегодня:\n\n"
    for key, item in stats.items():
        text += f"{key}: {item['today']}\n"

    await message.answer(text)
