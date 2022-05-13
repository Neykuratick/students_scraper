import asyncio

from database.applicants_crud import ApplicantsCRUD
from mpgu_api.applications import get_latest_applications

applicants_crud = ApplicantsCRUD()


async def main():

    applicants = await get_latest_applications()
    await applicants_crud.insert_many([applicant.dict() for applicant in applicants])
    applicant = await applicants_crud.get_one("fullNameGrid", "Ли Цуй")
    print(applicant)


asyncio.run(main())

# https://docs.google.com/document/d/1D4twRsfe0gMsUjo5RmswvJnY5mXIAtqLFfv8EKu8duo/edit
