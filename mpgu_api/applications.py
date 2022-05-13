from aiohttp_requests import requests


# https://pypi.org/project/aiohttp-requests/
from mpgu_api.models import Applicant


async def get_latest_applications() -> list[Applicant]:
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
        'Cookie': 'PHPSESSID=6ed2019a4705ad6d7abf0eddb9b9c084; _csrf=1cd7b370ccc5809e818fd2b9d790bb88196a3a212c60bba96d1d36e71fce72b4a%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22Cb8BhOpvQOHZjdZrQEzmv0WvAF7GEUtD%22%3B%7D',
        'X-CSRF-Token': 'yyWTL-_llAfwYLYd_5o13xFAPeotIxMqm7ubUD9qz5OIR6tth6rkcaEv_keV_m-tQAVHh1sTRFza_awXej-71w==',
    }

    response = await requests.post(url, headers=headers, data=payload)
    data = await response.json()

    applicants = []

    records = data.get("rows")
    for record in records:
        cell = record.get("cell")
        applicant_model = Applicant(**cell)

        applicants.append(applicant_model)

    return applicants
