from motor import motor_asyncio

# https://motor.readthedocs.io/en/stable/tutorial-asyncio.html
from pymongo.results import UpdateResult

from mpgu.models import Applicant


class ApplicantsCRUD:
    def __init__(self):
        conn_str = f"mongodb://127.0.0.1:27017"
        self._client = motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
        self._database = self._client.test_db

    async def get_one(self, key: str, value: str) -> Applicant:
        document = await self._database.test_collection.find_one(
            {key: value}
        )
        return Applicant(**document)

    async def insert_one(self, applicant: Applicant) -> UpdateResult:
        # https://stackoverflow.com/a/45685828

        document = applicant.dict()
        update = {"$set": document}

        return await self._database.test_collection.update_one(document, update, upsert=True)

    async def insert_many(self, applicants: list[Applicant]) -> list[UpdateResult]:
        result_applicants = []

        for applicant in applicants:
            result_applicant = await self.insert_one(applicant.dict())
            result_applicants.append(result_applicant)

        return result_applicants

    async def update_one(self, applicant: Applicant) -> UpdateResult:
        return await self._database.test_collection.update_one(
            {'id': applicant.id},
            {'$set': {**applicant.dict()}}
        )
