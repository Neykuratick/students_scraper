from datetime import datetime
from motor import motor_asyncio
from pymongo.results import UpdateResult
from mpgu.models import Applicant
# https://motor.readthedocs.io/en/stable/tutorial-asyncio.html


class ApplicantsCRUD:
    def __init__(self):
        conn_str = f"mongodb://127.0.0.1:27017"
        self._client = motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
        self._database = self._client.test_db
        self._collection = self._database.applicants

    async def get_one(self, key: str, value: str) -> Applicant | None:
        document = await self._collection.find_one({key: value})
        return Applicant(**document) if document else None

    async def insert_one(self, applicant: Applicant):
        document = applicant.dict()
        document['_inserted_at'] = datetime.now()

        existing_document = await self.get_one(key='id', value=str(applicant.id))

        if existing_document:
            return existing_document

        return await self._collection.insert_one(document)

    async def insert_many(self, applicants: list[Applicant]) -> list[UpdateResult]:
        result_applicants = []

        for applicant in applicants:
            result_applicant = await self.insert_one(applicant)
            result_applicants.append(result_applicant)

        return result_applicants

    async def update_one(self, applicant: Applicant) -> UpdateResult:
        document = applicant.dict()
        document['_updated_at'] = datetime.now()

        return await self._collection.update_one(
            {'id': applicant.id},
            {'$set': document}
        )
