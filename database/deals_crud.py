from datetime import datetime
from motor import motor_asyncio
from pymongo.results import UpdateResult

from amo_crm.models import Deal
# https://motor.readthedocs.io/en/stable/tutorial-asyncio.html


class DealsCRUD:
    def __init__(self):
        conn_str = f"mongodb://127.0.0.1:27017"
        self._client = motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
        self._database = self._client.scraper
        self._collection = self._database.deals

    async def get_one(self, key: str, value: str) -> Deal | None:
        document = await self._collection.find_one({key: value})
        return Deal(**document) if document else None

    async def insert_one(self, deal: Deal):
        document = deal.dict()
        document['_inserted_at'] = datetime.now()

        existing_document = await self.get_one(key='id', value=str(deal.application_id))

        if existing_document:
            return existing_document

        return await self._collection.insert_one(document)

    async def insert_many(self, deals: list[Deal]) -> list[UpdateResult]:
        result_deals = []

        for deal in deals:
            result_deal = await self.insert_one(deal)
            result_deals.append(result_deal)

        return result_deals

    async def update_one(self, deal: Deal) -> UpdateResult:
        document = deal.dict()
        document['_updated_at'] = datetime.now()

        return await self._collection.update_one(
            {'id': deal.application_id},
            {'$set': document}
        )
