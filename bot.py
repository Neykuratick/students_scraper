from bot.binding import get_root
from config import settings
from aiogram import Bot

if __name__ == '__main__':
    root_router = get_root()
    bot = Bot(token=settings.BOT_TOKEN)
    root_router.run_polling(bot)
