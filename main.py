from bot.start import authenticate
from database.deals_crud import DealsCRUD
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs.amocrm import run_deals
from jobs.mpgu import store_deals
from aiogram import executor
from bot.misc import dp

db = DealsCRUD()

scheduler = AsyncIOScheduler(timezone='UTC', daemon=True)
scheduler.add_job(store_deals, 'interval', [db], seconds=3)
# scheduler.add_job(run_deals, 'interval', [db], seconds=3)
scheduler.start()


if __name__ == '__main__':
    dp.register_message_handler(authenticate, commands=['start'])
    executor.start_polling(dp)


"""
TODO
--
1. Unhardcode refresh token
2. Telegram bots
"""