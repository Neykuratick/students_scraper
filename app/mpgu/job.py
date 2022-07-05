from app.amo_crm.models import Deal
from app.database.deals_crud import db
from app.mpgu.actualizer import get_contract_statuses
from app.mpgu.api import get_latest_deals, get_applicants_data, get_item
from pymongo.results import InsertOneResult


def compose_new_values(deal: Deal, old_deal: Deal):
    new_values = {}
    if deal.snils is not None and deal.snils != old_deal.snils:
        new_values['snils'] = deal.snils

    if deal.current_status is not None and deal.current_status != old_deal.current_status:
        new_values['current_status'] = deal.current_status

    if deal.mpgu_contract_date is not None and deal.mpgu_contract_date != old_deal.mpgu_contract_date:
        new_values['mpgu_contract_date'] = deal.mpgu_contract_date

    if deal.mpgu_contract_number is not None and deal.mpgu_contract_number != old_deal.mpgu_contract_number:
        new_values['mpgu_contract_number'] = deal.mpgu_contract_number

    return new_values


async def store_deals():
    print('done')
    applicants_data = await get_applicants_data()
    async for deal in get_latest_deals():
        if "Иностр" in deal.contact.competitive_group:
            continue

        snils = get_item(applicants_data, 'id', deal.applicant_id)
        deal.snils = snils
        result = await db.insert_one(deal)

        old_deal = await db.get_one("application_id", deal.application_id)

        new_values = compose_new_values(deal=deal, old_deal=old_deal)

        if result == 'exists':
            if new_values:
                print(f'MPGU_DATABASE: updating values: {new_values=}')
                await db.safe_update_one(
                    application_id=deal.application_id,
                    new_values=new_values
                )

        if isinstance(result, InsertOneResult):
            continue

        else:
            raise RuntimeError(f'Unknown result. {result=}')


async def actualize_contracts():
    async for fio, contract_status in get_contract_statuses():
        async for deal in db.get(name=fio):
            if contract_status is None:
                continue

            await db.safe_update_one(
                application_id=deal.application_id,
                new_values={"contract_status": contract_status}
            )
