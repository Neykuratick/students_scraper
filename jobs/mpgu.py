from typing import AsyncIterable
from amo_crm.models import Deal, Contact, Company
from database.deals_crud import DealsCRUD
from mpgu.api import get_latest_applications


async def get_deals() -> AsyncIterable[Deal]:
    async for applicant in get_latest_applications():
        contact = Contact(
            name=applicant.fullNameGrid,
            first_name=applicant.first_name,
            last_name=applicant.last_name,
            phone_number=applicant.incoming_phone_mobile,
            email=applicant.incoming_email,
            competitive_group=applicant.competitiveGroup_name
        )

        yield Deal(
            applicant_id=applicant.incoming_id,
            application_id=applicant.id,
            company=Company(website=applicant.web_url),
            contact=contact
        )


async def store_deals(db: DealsCRUD):
    async for deal in get_deals():
        print(f"\n\n{deal=}\n\n")
        await db.insert_one(deal)
