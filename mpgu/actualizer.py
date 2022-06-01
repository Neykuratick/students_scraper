from typing import AsyncIterable

import requests
from bs4 import BeautifulSoup
from config import mpgu_headers


async def parse_table(table) -> AsyncIterable[list[str, str]]:
    x = (len(table.findAll('tr')))
    for index, row in enumerate(table.findAll('tr')[1:x]):
        col = row.findAll('td')
        fio = col[2].getText()
        contract_status = col[5].getText()
        yield [fio, contract_status]


async def get_contract_statuses() -> AsyncIterable[list[str, str]]:
    """
        Если у абитуриента будет совпадать ФИО, обновится контракт только у каждого найденного
        Поэтому поиск должен быть по contract_id, а не fio. И фукнция айди контракта долдна отдавать
    """
    page = 1850  # TODO поменять на более актуальную страницу на проде

    while True:
        page += 1

        r = requests.post(f'https://dbs.mpgu.su/abiturient/contract?page={page}', headers=mpgu_headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table')

        async for result_list in parse_table(table):
            yield result_list

        if 'next disabled' in r.text:
            break
