from aiogram import Bot, Dispatcher
from config import settings

dp = Dispatcher(Bot(token=settings.BOT_TOKEN))
