from database.applicants_crud import ApplicantsCRUD
from mpgu.api import get_latest_applications
from deepdiff import DeepDiff


async def actualize(applicants_crud: ApplicantsCRUD):
    async for new_applicant in get_latest_applications():
        old_applicant = await applicants_crud.get_one('id', new_applicant.id)

        diff = DeepDiff(new_applicant.dict(), old_applicant.dict())
        if not diff:
            continue

        # Если абитуриент поменялся, обновляем его заявку целиком
        await applicants_crud.update_one(new_applicant)

