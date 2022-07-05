from datetime import datetime
from typing import Any, AsyncIterable
from motor import motor_asyncio
from pymongo.results import UpdateResult
from app.amo_crm.models import Deal
from config import settings


class DealsCRUD:
    def __init__(self):
        conn_str = f"mongodb://{settings.DB_HOST}:27017"
        self._client = motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
        self._database = self._client.scraper
        self._collection = self._database.deals

    async def get_one(self, key: str, value: Any) -> Deal | None:
        document = await self._collection.find_one({key: value})
        return Deal(**document) if document else None

    async def get(
            self,
            inserted_date: datetime = None,
            modified_date: datetime = None,
            mpgu_contract_date: datetime = None,
            applicant_id: int = None,
            name: str = None
    ) -> AsyncIterable[Deal]:
        if modified_date:
            filter_ = {"updated_at": {"$gt": modified_date}}
        elif inserted_date:
            filter_ = {"inserted_at": {"$gt": inserted_date}}
        elif mpgu_contract_date:
            filter_ = {'mpgu_contract_date': {'$gt': mpgu_contract_date}}
        elif applicant_id:
            filter_ = {"applicant_id": {"$eq": applicant_id}}
        elif name:
            filter_ = {"contact.name": {"$regex": f"^{name}"}}
        else:
            filter_ = {}

        async for doc in self._collection.find(filter=filter_):
            yield Deal(**doc)

    async def insert_one(self, deal: Deal):
        document = deal.dict()
        document['inserted_at'] = datetime.now()
        document['updated_at'] = datetime.now()

        existing_document = await self.get_one(key='application_id', value=deal.application_id)
        if existing_document:
            return 'exists'

        return await self._collection.insert_one(document)

    async def safe_update_one(
        self,
        application_id: int,
        new_values: dict
    ):
        new_values['updated_at'] = datetime.now()
        return await self._collection.update_one(
            {'application_id': application_id},
            {'$set': new_values}
        )

    async def actualize_uploaded_at(self, deal: Deal, crm_id: str = None) -> UpdateResult:
        if crm_id:
            set_dict = {'uploaded_at': datetime.now(), 'crm_id': crm_id}
        else:
            set_dict = {'uploaded_at': datetime.now()}

        return await self._collection.update_one(
            {'application_id': deal.application_id},
            {'$set': set_dict}
        )

    async def find_all_competitive_groups(self, applicant_id: int) -> str:
        groups = []
        async for deal in self.get(applicant_id=applicant_id):
            group = deal.contact.competitive_group
            if group not in groups:
                groups.append(group)

        return ", ".join(groups) if len(groups) > 0 else ""


db = DealsCRUD()
