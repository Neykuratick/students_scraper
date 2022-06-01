from aiogram import Dispatcher

from bot.daily_stats.handler import daily_stats_router
from bot.get_statistic.handler import statistics_router
from bot.auth.handler import auth_router


def get_root():
    root_db = Dispatcher()
    root_db.include_router(daily_stats_router)
    root_db.include_router(statistics_router)
    root_db.include_router(auth_router)

    return root_db
