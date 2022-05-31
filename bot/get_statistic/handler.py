from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.router import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from magic_filter import F
from bot.get_statistic.callbacks import DealCallback, CompetitiveGroupCallback
from bot.get_statistic.maps import majors_map_system
from bot.get_statistic.services import find_deals_by_name, humanize_competitive_group, get_statistic
from bot.states import Form

statistics_router = Router()


@statistics_router.message(Form.deal)
async def process_name(message: Message, state: FSMContext):
    name = message.text.lower().title()
    deals = await find_deals_by_name(name=name)

    if len(deals) < 1:
        await message.answer(
            f'🤷‍♀️ Такого абитуриента не нашлось :с\n\nВозможно, {name} ещё не попал(а) в базу бота'
        )
        await state.clear()
        return

    buttons = []
    for index, deal in enumerate(deals):
        callback = DealCallback(deal_id=index)
        button = InlineKeyboardButton(text=f'💁 {deal.contact.name}', callback_data=callback.pack())
        buttons.append([button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer("🔎 Теперь выбери себя в списке", reply_markup=keyboard)
    await state.set_state(Form.competitive_group)
    await state.update_data(message=message, deals=deals)


@statistics_router.callback_query(
    DealCallback.filter((F.action == '1')),
)
async def process_name_callback(query: CallbackQuery, callback_data: DealCallback, state: FSMContext):
    await query.answer('Готово!')
    await state.set_state(Form.competitive_group)

    data = await state.get_data()
    message = data['message']
    deal = data['deals'][callback_data.deal_id]

    groups = await humanize_competitive_group(deal=deal)

    if len(groups) < 1:
        await message.answer(
            f'🤷‍♀️ Конкурсные списки не нашлись :с'
            f'\n\nВозможно, {deal.contact.name} подавал(а) документы на те направления, про которые бот не знает'
        )
        return

    buttons = []
    for index, group in enumerate(groups):
        callback = CompetitiveGroupCallback(group_id=index)
        button = InlineKeyboardButton(text=f'✅ {group}', callback_data=callback.pack())
        buttons.append([button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(
        f'🔎 А теперь выбери направление, для которого ты хочешь узнать статистику для абитуриента {deal.contact.name}',
        reply_markup=keyboard
    )

    await state.set_state(Form.display_data)
    await state.update_data(deal_id=callback_data.deal_id, groups=groups)


@statistics_router.callback_query(
    CompetitiveGroupCallback.filter((F.action == '2')),
    Form.display_data
)
async def process_name_callback(query: CallbackQuery, callback_data: CompetitiveGroupCallback, state: FSMContext):
    group_id = callback_data.group_id

    data = await state.get_data()
    message = data['message']
    deal = data['deals'][data['deal_id']]
    group = data['groups'][group_id]

    await query.answer('Готово')
    await message.answer(
        f'👨‍💻 Пытаюсь собрать статистику по направлению "{group}"'
        f'\n\n⏳ Это может занять продолжительное время, в зависимости от популярности направления',
    )

    group_id = majors_map_system.get(group)
    text = f'📈 Готово! Вот статистика для абитуриента {deal.contact.name}:\n\n'
    text += await get_statistic(snils=deal.snils, group_id=group_id)

    await message.answer(text)
