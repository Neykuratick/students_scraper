import requests
from aiogram import Dispatcher
from aiogram.types import Message
from bs4 import BeautifulSoup

from amo_crm.models import Deal
from bot.get_statistic.maps import majors_map_human, majors_map_system
from database.deals_crud import db

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

    found_scores = -9999

    # variable to check length of rows
    x = (len(table.findAll('tr')))
    # set to run through x
    for row in table.findAll('tr')[1:x]:
        col = row.findAll('td')
        website_snils = col[1].getText()
        total_scores = col[10].getText()  # Для платных направлений - это 11 столбик
        agreement = col[8].getText()  # + true, - false
        print(agreement)
        if snils == website_snils:
            found_scores = total_scores
            break

    if found_scores == -9999:
        return 'Ничего не нашлось('

    return f"{found_scores=}, {snils=}"


async def compose_message(group: str, snils: str) -> str:
    group_id = majors_map_system.get(group)
    return await get_statistic(snils=snils, group_id=group_id)
