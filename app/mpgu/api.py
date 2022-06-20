from math import ceil
from typing import AsyncIterable
from aiohttp_requests import requests
from app.amo_crm.models import Deal, Contact, Company
from app.mpgu.token_manager import token_manager
from app.mpgu.models import Applicant


def get_item(collection, key, target):
    for item in collection:
        if item[key] == target:
            return item['cell'].get('snils')


async def get_rows() -> int:
    url = "https://dbs.mpgu.su/incoming_2022/application/jqgrid?action=request"

    payload = "_search=true" \
              "&nd=1652592848886" \
              "&rows=1" \
              "&page=9999999999" \
              '&filters={"groupOp":"AND","rules":[{"field":"competitiveGroup.name","op":"cn","data":"ИМО |"}]}' \
              "&visibleColumns[]=id" \

    try:
        response = await requests.post(url, headers=token_manager.get_headers(), data=payload)
        data = await response.json()
        return data.get('records')
    except Exception as e:
        print(f'Error in get rows: {e}')
        return 0


async def _get_applicants(page, rows) -> AsyncIterable[Applicant]:
    url = "https://dbs.mpgu.su/incoming_2022/application/jqgrid?action=request"

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
              "&visibleColumns[]=incoming_id" \
              "&visibleColumns[]=snils" \
              "&visibleColumns[]=contract.number" \
              "&visibleColumns[]=contract.date" \

    try:
        response = await requests.post(url, headers=token_manager.get_headers(), data=payload)
        data = await response.json()
        records = data.get("rows")
    except Exception as e:
        print(f'Error in get applicants: {e}')
        return

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

    for page in range(pages + 1):
        async for applicant in _get_applicants(page, step):
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
                snils=applicant.snils,
                company=Company(website=applicant.web_url),
                contact=contact,
                current_status=applicant.current_status,
                mpgu_contract_number=applicant.contract_number,
                mpgu_contract_date=applicant.contract_date
            )

            yield deal


async def get_applicants_data() -> list:
    url = "https://dbs.mpgu.su/incoming_2022/jqgrid?action=request"

    payload = "_search=false" \
              "&nd=1653831681755" \
              "&rows=1" \
              "&page=1" \
              "&visibleColumns[]=id" \
              "&visibleColumns[]=snils" \

    response = await requests.post(url, headers=token_manager.get_headers(), data=payload)
    data = await response.json()
    records = data['records']
    pages = ceil(records / 10000)

    returning_data = []

    for page in range(1, pages + 1):
        payload = "_search=false" \
                  "&nd=1653831681755" \
                  "&rows=10000" \
                  f"&page={page}" \
                  "&visibleColumns[]=id" \
                  "&visibleColumns[]=snils" \

        response = await requests.post(url, headers=token_manager.get_headers(), data=payload)
        data = await response.json()
        rows = data.get('rows')

        returning_data += rows

    return returning_data
