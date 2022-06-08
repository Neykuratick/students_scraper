from aiogram.dispatcher.filters.callback_data import CallbackData


class DealCallback(CallbackData, prefix='1'):
    action: str = "1"
    deal_id: int


class CompetitiveGroupCallback(CallbackData, prefix='2'):
    action: str = "2"
    group_id: int
