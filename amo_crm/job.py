import asyncio
from amo_crm.api import AmoCrmApi
from amo_crm.models import Deal
from database.deals_crud import DealsCRUD
from datetime import datetime


async def patch_deal(deal: Deal, db: DealsCRUD, amo: AmoCrmApi):
    groups = await db.find_all_competitive_groups(applicant_id=deal.applicant_id)
    patch_result = await amo.patch_deal(deal=deal, new_competitive_group=groups)
    return patch_result


def is_new(deal: Deal) -> bool:
    if deal.uploaded_at is None:
        return True

    return False


def is_updated(deal: Deal) -> bool:
    if isinstance(deal.uploaded_at, datetime) and isinstance(deal.updated_at, datetime):
        if deal.updated_at > deal.uploaded_at:
            return True

    return False


async def run_deals(db: DealsCRUD):
    i = 0

    amo = AmoCrmApi()

    async for deal in db.get():
        i += 1

        if is_new(deal=deal):
            result = await amo.create_deal(deal)
        elif is_updated(deal=deal):
            result = await patch_deal(deal=deal, db=db, amo=amo)
        else:
            print(f'INFO: Deal exists and is up to date. {i=}, {deal=}')
            continue

        if result.get('detail') == 'duplicate':
            result = await patch_deal(deal=deal, db=db, amo=amo)

        if result.get('detail') == 'success':
            crm_deal_id = result.get('deal_id')
            await db.actualize_uploaded_at(deal=deal, crm_id=crm_deal_id)

        print(
            f"DEBUG: RUN_DEALS: {i=}, AmoCrmEntityId={crm_deal_id}, {is_new(deal)=},  "
            f"{is_updated(deal)=}, Deal={deal.dict()}"
        )
