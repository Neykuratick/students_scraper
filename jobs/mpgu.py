from database.deals_crud import DealsCRUD
from mpgu.api import get_latest_deals, get_applicants_data, get_item


async def store_deals(db: DealsCRUD):
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
