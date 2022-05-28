from database.deals_crud import DealsCRUD
from mpgu.api import get_latest_deals


async def store_deals(db: DealsCRUD):
    print('done')
    async for deal in get_latest_deals():
        result = await db.insert_one(deal)

        if "Иностр" in deal.contact.competitive_group:
            continue

        if result == 'exists':
            await db.update_one(deal=deal)
