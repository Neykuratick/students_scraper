from math import ceil
from typing import AsyncIterable

from aiohttp_requests import requests


# https://pypi.org/project/aiohttp-requests/
from amo_crm.models import Deal, Contact, Company
from config import settings
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
        'Cookie': settings.TEMP_COOKIE,
        'X-CSRF-Token': settings.TEMP_MPGU_TOKEN
    }

    response = await requests.post(url, headers=headers, data=payload)
    data = await response.json()

    return data.get('records')


async def _get_applicants(page, rows) -> AsyncIterable[Applicant]:
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
        'Cookie': settings.TEMP_COOKIE,
        'X-CSRF-Token': settings.TEMP_MPGU_TOKEN
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


async def get_latest_deals() -> AsyncIterable[Deal]:
    step = 90

    rows = await get_rows()
    pages = ceil(rows / step)

    async for page in async_range(pages):
        requesting_rows = step if step < rows else rows

        async for applicant in _get_applicants(page, requesting_rows):
            contact = Contact(
                name=applicant.fullNameGrid,
                first_name=applicant.first_name,
                last_name=applicant.last_name,
                phone_number=applicant.incoming_phone_mobile,
                email=applicant.incoming_email,
                competitive_group=applicant.competitiveGroup_name
            )

            deal = Deal(
                applicant_id=applicant.incoming_id,
                application_id=applicant.id,
                company=Company(website=applicant.web_url),
                contact=contact
            )

            yield deal

        rows -= requesting_rows
