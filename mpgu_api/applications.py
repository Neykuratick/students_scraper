from aiohttp_requests import requests


# https://pypi.org/project/aiohttp-requests/
from mpgu_api.models import Applicant


async def get_latest_applications():
    url = "https://dbs.mpgu.su/incoming_2021/application/jqgrid?action=request"

    payload = "_search=false" \
              "&nd=1652449396830" \
              "&rows=30" \
              "&page=1" \
              "&sidx=id" \
              "&sord=desc" \
              "&visibleColumns%5B%5D=id" \
              "&visibleColumns%5B%5D=fullNameGrid" \
              "&visibleColumns%5B%5D=application_code" \
              "&visibleColumns%5B%5D=competitiveGroup.name" \
              "&visibleColumns%5B%5D=application_number" \
              "&visibleColumns%5B%5D=vi_status" \
              "&visibleColumns%5B%5D=current_status_id" \
              "&visibleColumns%5B%5D=incoming.incoming_type_id" \
              "&visibleColumns%5B%5D=competitiveGroup.education_level_id" \
              "&visibleColumns%5B%5D=fok_status" \
              "&visibleColumns%5B%5D=incoming_id"

    headers = {
        'Cookie': 'PHPSESSID=711ca715cc999401c28e1dc97a6316bf; _csrf=ba3acaea8ba8cd52ffc198396519bf1705f0f4279ce7c456c1c71e06b17ae95ba%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22S7-Qd9W1uDhfVOM26rJsV9KwUyWfLUvB%22%3B%7D',
        'X-CSRF-Token': '9NDLlF4YTgH8xCyV-7HYEsm45GqGwpE4cYSNv3GUJ8un5-bFOiEZMImARPOt_pUg_8quGdD72k8k_drZPcFRiQ==',
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



