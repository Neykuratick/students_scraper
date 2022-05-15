import asyncio

from database.applicants_crud import ApplicantsCRUD
from mpgu.actualizer import actualize
from mpgu.api import get_latest_applications


async def main():
    applicants_crud = ApplicantsCRUD()
    # await actualize(applicants_crud)
    #
    i = 1
    async for applicant in get_latest_applications():
        print(i, applicant)
        i += 1

    # applicant = await applicants_crud.get_one("fullNameGrid", "Ли Цуй")
    # print(applicant)


asyncio.run(main())

# https://docs.google.com/document/d/1D4twRsfe0gMsUjo5RmswvJnY5mXIAtqLFfv8EKu8duo/edit
