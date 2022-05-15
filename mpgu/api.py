from math import ceil

from aiohttp_requests import requests


# https://pypi.org/project/aiohttp-requests/
from mpgu.models import Applicant
from utils import async_range


async def get_rows():
    url = "https://dbs.mpgu.su/incoming_2021/application/jqgrid?action=request"

    payload = "_search=true" \
              "&nd=1652592848886" \
              "&rows=1" \
              "&page=9999999999" \
              '&filters={"groupOp":"AND","rules":[{"field":"competitiveGroup.name","op":"cn","data":"ИМО |"}]}' \
              "&visibleColumns[]=id" \

    headers = {
        'Cookie': 'PHPSESSID=72f1faa3fd7a218d2064f83c16acd8cd; _csrf=9b280518a610a3c2ec79da076099a0b72ce70258149ddd2ed98bb1aa8f45ee02a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22dlw6gd6miFgBGqTtpGh7Qm7qhJUWoDTz%22%3B%7D',
        'X-CSRF-Token': 'RIG3DJXyolmB1vB1jaPxK2PxkqrSYpoGi1MtCoLG1cEg7cA68paUNOiQlzfK0qVfE7b6nYMPrXfjGXhd7YKBuw==',
    }

    response = await requests.post(url, headers=headers, data=payload)
    data = await response.json()

    return data.get('records')


async def _get_applicants(page, rows):
    url = "https://dbs.mpgu.su/incoming_2021/application/jqgrid?action=request"

    payload = "_search=true" \
              "&nd=1652592848886" \
              f"&rows={rows}" \
              f"&page={page}" \
              "&sidx=" \
              "&sord=asc" \
              '&filters={"groupOp":"AND","rules":[{"field":"competitiveGroup.name","op":"cn","data":"ИМО |"}]}' \
              "&visibleColumns[]=id" \
              "&visibleColumns[]=fullNameGrid" \
              "&visibleColumns[]=application_code" \
              "&visibleColumns[]=competitiveGroup.name" \
              "&visibleColumns[]=application_number" \
              "&visibleColumns[]=current_status_id" \
              "&visibleColumns[]=incoming.email" \
              "&visibleColumns[]=incoming.phone_mobile" \
              "&visibleColumns[]=competitiveGroup.financing_type_id" \
              "&visibleColumns[]=incoming_id"

    headers = {
        'Cookie': 'PHPSESSID=72f1faa3fd7a218d2064f83c16acd8cd; _csrf=9b280518a610a3c2ec79da076099a0b72ce70258149ddd2ed98bb1aa8f45ee02a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22dlw6gd6miFgBGqTtpGh7Qm7qhJUWoDTz%22%3B%7D',
        'X-CSRF-Token': 'RIG3DJXyolmB1vB1jaPxK2PxkqrSYpoGi1MtCoLG1cEg7cA68paUNOiQlzfK0qVfE7b6nYMPrXfjGXhd7YKBuw==',
    }

    response = await requests.post(url, headers=headers, data=payload)
    data = await response.json()

    records = data.get("rows")

    if records is None:
        print(f"ERROR: {data}")
        return

    for record in records:
        cell = record.get("cell")
        applicant_model = Applicant(**cell)

        yield applicant_model


async def get_latest_applications():
    step = 90

    rows = await get_rows()
    pages = ceil(rows / step)

    async for page in async_range(pages):
        requesting_rows = step if step < rows else rows

        async for applicant in _get_applicants(page, requesting_rows):
            yield applicant

        rows -= requesting_rows



