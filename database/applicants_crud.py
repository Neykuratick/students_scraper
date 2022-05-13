from motor import motor_asyncio

# https://motor.readthedocs.io/en/stable/tutorial-asyncio.html
from mpgu_api.models import Applicant


class ApplicantsCRUD:
    def __init__(self):
        conn_str = f"mongodb://127.0.0.1:27017"
        self.client = motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
        self.database = self.client.test_db

    async def insert_one(self, document: dict):
        result = await self.database.test_collection.insert_one(document)
        return result

    async def insert_many(self, documents: list[dict]):
        result_documents = []

        for document in documents:
            result_document = await self.insert_one(document)
            result_documents.append(result_document)

        return result_documents

    async def get_one(self, key: str, value: str) -> Applicant:
        document = await self.database.test_collection.find_one({key: value})
        print(document)
        # TODO return applicant
