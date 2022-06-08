from aiogram.types import Message
from datetime import datetime, timedelta
from aiogram.dispatcher.router import Router
from app.database.deals_crud import db

daily_stats_router = Router()


def compose_applications_total(stats: dict) -> str:
    text = "📈 Всего заявок:\n\n"
    inner_text = ''
    for key, item in stats.items():
        total = item.get('total')
        inner_text += f"{key}: {total}\n" if total is not None else ""

    if not inner_text:
        return ''

    return text + inner_text


def compose_contracts_today(stats: dict) -> str:
    text = "\n📝 Контрактов за сегодня:\n\n"
    inner_text = ''
    for key, item in stats.items():
        total = item.get('today_contracts')
        inner_text += f"{key}: {total}\n" if total is not None else ""

    if not inner_text:
        return text + 'За сегодня не поступило контрактов\n'

    return text + inner_text


def compose_applications_today(stats: dict) -> str:
    text = "\n📆 Заявок за сегодня:\n\n"
    inner_text = ''
    for key, item in stats.items():
        total = item.get('today')
        inner_text += f"{key}: {total}\n" if total is not None else ""

    if not inner_text:
        return text + 'За сегодня не поступило заявок\n'

    return text + inner_text


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

    async for deal in db.get(inserted_date=datetime.today() - timedelta(days=1)):
        count = stats.get(deal.contact.competitive_group).get('today') or 0
        stats[deal.contact.competitive_group]['today'] = count + 1

    async for deal in db.get(mpgu_contract_date=datetime.today() - timedelta(days=1)):
        count = stats.get(deal.contact.competitive_group).get('today_contracts') or 0
        stats[deal.contact.competitive_group]['today_contracts'] = count + 1

    applications_total = compose_applications_total(stats)
    applications_today = compose_applications_today(stats)
    contracts_today = compose_contracts_today(stats)

    text = applications_total + applications_today + contracts_today

    await message.answer(text)
