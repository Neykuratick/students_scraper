import asyncio
import pymongo

from amo_crm.api import AmoCrmApi
from amo_crm.models import Finances, Contact, Company, Deal
from database.applicants_crud import ApplicantsCRUD
from mpgu.actualizer import actualize
from mpgu.api import get_latest_applications


async def main():
    api = AmoCrmApi()

    async for applicant in get_latest_applications():
        contact = Contact(
            name=applicant.fullNameGrid,
            first_name=applicant.first_name,
            last_name=applicant.last_name,
            phone_number=applicant.incoming_phone_mobile,
            email=applicant.incoming_email,
            competitive_group=applicant.competitiveGroup_name
        )

        company = Company(
            website=applicant.web_url
        )

        await api.create_deal(
            deal=Deal(
                contact=contact,
                company=company
            )
        )


asyncio.run(main())

# https://docs.google.com/document/d/1D4twRsfe0gMsUjo5RmswvJnY5mXIAtqLFfv8EKu8duo/edit

#
# from amocrm.v2 import tokens
#
# tokens.default_token_manager(
#     client_id=settings.AMO_CLIENT_ID,
#     client_secret=settings.AMO_CLIENT_SECRET,
#     subdomain=settings.AMO_SUBDOMAIN,
#     redirect_url=settings.AMO_REDIRECT_URL,
#     storage=tokens.FileTokensStorage(),  # by default FileTokensStorage
# )
# tokens.default_token_manager.init(code=settings.AMO_AUTH_CODE, skip_error=True)
