import requests
from aiogram import Dispatcher
from bs4 import BeautifulSoup

from app.amo_crm.models import Deal
from app.bot.get_statistic.maps import majors_map_human, MajorsEnum
from app.database.deals_crud import db

statistics_dp = Dispatcher()


def check_deal_exists(collection: list, deal: Deal):
    for existing_deal in collection:
        if existing_deal.snils == deal.snils:
            return True

    return False


async def humanize_competitive_group(deal: Deal) -> list[str]:
    groups_str = await db.find_all_competitive_groups(applicant_id=deal.applicant_id)
    groups = groups_str.split(', ')
    returning_groups = []

    for group in groups:
        human_group = majors_map_human.get(group)

        if human_group is None:
            continue

        if human_group not in returning_groups:
            returning_groups.append(human_group)

    return returning_groups


async def find_deals_by_name(name: str) -> list[Deal]:
    deals = []
    async for deal in db.get(name=name):
        deal_exists = check_deal_exists(collection=deals, deal=deal)

        if deal_exists is True:
            continue

        deals.append(deal)

    return deals


async def get_statistic(snils: str, group_id: int) -> str:
    r = requests.get(f"https://sdo.mpgu.org/competition-list/entrant-list?cg={group_id}&type=list")
    print(f"https://sdo.mpgu.org/competition-list/entrant-list?cg={group_id}&type=list")
    print(snils)

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table')

    try:
        budget_seats_str = soup.find("span", text="Контрольные цифры приема:").next_sibling
        budget_seats = int(budget_seats_str.replace(' ', ''))
    except Exception:
        budget_seats = -9999

    if group_id in [MajorsEnum.JUR_INT_JUR, MajorsEnum.MANAGEMENT]:
        # Если направление платное
        total_scores_id = 11
    else:
        total_scores_id = 10

    people_above = -9999
    found_scores = -9999
    agreements = 0

    x = (len(table.findAll('tr')))
    for index, row in enumerate(table.findAll('tr')[1:x]):
        col = row.findAll('td')

        website_snils = col[1].getText()
        total_scores = col[total_scores_id].getText()
        agreement = col[8].getText().strip()  # + true, - false
        if '+' in agreement:
            agreements += 1

        if snils == website_snils:
            found_scores = total_scores
            people_above = index

            break

    if found_scores == -9999:
        return 'Ничего не нашлось('

    has_budget_seats = budget_seats > -1
    has_chance = agreements < budget_seats

    text = f"Итоговых баллов: {found_scores}"
    text += f"\nАбитуриентов перед тобой: {people_above}"
    text += f"\nИз них подали согласие на зачисление: {agreements}"
    text += f"\nВсего бюджетных мест: {budget_seats}" if has_budget_seats else ""
    text += f"\n\nКажется, по этому направлению ты уже не пройдёшь 😢" if not has_chance and has_budget_seats else ""
    text += f"\n\nУ тебя ещё есть шансы!! 🥳" if has_chance and has_budget_seats else ""

    return text
