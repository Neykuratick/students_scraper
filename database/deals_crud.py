from datetime import datetime
from typing import Any
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

    async def get_one(self, key: str, value: Any) -> Deal | None:
        document = await self._collection.find_one({key: value})
        return Deal(**document) if document else None

    async def get(self, modified_date: datetime = None):
        if modified_date:
            filter_ = {"_updated_at": {"$lt": datetime.now()}}
        else:
            filter_ = {}

        async for doc in self._collection.find(filter=filter_):
            yield Deal(**doc)

    async def insert_one(self, deal: Deal):
        document = deal.dict()
        document['_inserted_at'] = datetime.now()

        existing_document = await self.get_one(key='application_id', value=deal.application_id)
        if existing_document:
            return existing_document

        return await self._collection.insert_one(document)

    async def update_one(self, deal: Deal) -> UpdateResult:
        document = deal.dict()
        document['_updated_at'] = datetime.now()

        return await self._collection.update_one(
            {'application_id': deal.application_id},
            {'$set': document}
        )
