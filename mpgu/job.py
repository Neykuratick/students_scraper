from database.deals_crud import db
from mpgu.actualizer import get_contract_statuses
from mpgu.api import get_latest_deals, get_applicants_data, get_item


async def store_deals():
    print('done')
    applicants_data = await get_applicants_data()
    async for deal in get_latest_deals():
        if "Иностр" in deal.contact.competitive_group:
            continue

        snils = get_item(applicants_data, 'id', deal.applicant_id)
        deal.snils = snils
        result = await db.insert_one(deal)

        if result == 'exists':
            await db.update_one(deal=deal)


async def actualize_contracts():
    async for fio, contract_status in get_contract_statuses():
        async for deal in db.get(name=fio):
            deal.contract_status = contract_status
            await db.update_one(deal=deal)
