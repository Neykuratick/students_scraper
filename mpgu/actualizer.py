import requests
from bs4 import BeautifulSoup
from config import mpgu_headers


def parse_table(table):
    x = (len(table.findAll('tr')))
    for index, row in enumerate(table.findAll('tr')[1:x]):
        col = row.findAll('td')
        fio = col[2].getText()
        contract_status = col[5].getText()

        return fio, contract_status


async def get_contract_statuses():
    page = 1900  # TODO поменять на более актуальную страницу на проде

    while True:
        page += 1

        r = requests.post(f'https://dbs.mpgu.su/abiturient/contract?page={page}', headers=mpgu_headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table')
        parse_table(table)

        if 'next disabled' in r.text:
            break
