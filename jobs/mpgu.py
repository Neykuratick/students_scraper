from database.deals_crud import DealsCRUD
from mpgu.api import get_latest_deals


async def store_deals(db: DealsCRUD):
    async for deal in get_latest_deals():
        await db.insert_one(deal)
