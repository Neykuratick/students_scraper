import asyncio
import pymongo
from database.applicants_crud import ApplicantsCRUD
from mpgu.actualizer import actualize
from mpgu.api import get_latest_applications


async def main():
    applicants_crud = ApplicantsCRUD()

    async for applicant in get_latest_applications():
        await applicants_crud.insert_one(applicant)

    # applicant = await applicants_crud.get_one("fullNameGrid", "Ли Цуй")
    # print(applicant)


asyncio.run(main())

# https://docs.google.com/document/d/1D4twRsfe0gMsUjo5RmswvJnY5mXIAtqLFfv8EKu8duo/edit
