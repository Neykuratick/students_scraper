from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import settings
from jobs.amocrm import run_deals
from jobs.mpgu import store_deals
from aiogram import Bot
from bot.binding import get_root

scheduler = AsyncIOScheduler(timezone='UTC', daemon=True)
# scheduler.add_job(store_deals, 'interval', [db], seconds=3)
# scheduler.add_job(run_deals, 'interval', [db], seconds=3)
scheduler.start()


if __name__ == '__main__':
    root_router = get_root()
    bot = Bot(token=settings.BOT_TOKEN)
    root_router.run_polling(bot)


"""
TODO
--
1. Unhardcode refresh token
2. Telegram bots
"""