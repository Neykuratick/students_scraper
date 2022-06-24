from app.amo_crm.api import AmoCrmApi
from app.amo_crm.models import Deal
from app.amo_crm.models import GetDeal
from app.database.deals_crud import db
from datetime import datetime


async def patch_deal(deal: Deal, amo: AmoCrmApi):
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


async def run_deals():
    i = 0

    amo = AmoCrmApi()

    async for deal in db.get():
        i += 1

        if is_new(deal=deal):
            print(f'INFO: Uploading new {deal=}')
            result = await amo.create_deal(deal)
        elif is_updated(deal=deal):
            print(f'INFO: Updating {deal=}')
            result = await patch_deal(deal=deal, amo=amo)
        else:
            # print(f'INFO: Deal exists and is up to date. {i=}, {deal=}')
            continue

        if result.get('detail') == 'duplicate':
            result = await patch_deal(deal=deal, amo=amo)

        if result.get('detail') == 'success':
            crm_deal_id = result.get('deal_id')
            await db.actualize_uploaded_at(deal=deal, crm_id=crm_deal_id)

        print(
            f"DEBUG: RUN_DEALS: {i=}, AmoCrmEntityId={crm_deal_id}, {is_new(deal)=},  "
            f"{is_updated(deal)=}, Deal={deal.dict()}"
        )


async def process_pipeline_statuses():
    amo = AmoCrmApi()

    status_map = {
        0: 40586119,
        1: 40586116,
        2: 40582720,
        3: 143
    }

    # статусы, сделки по которым необходимо игнорировать, если
    # статус абитуриента не поменялся на "согласие на зачисление" или "Сформирован"

    order_map = {
        # чем ниже статус, тем он главнее. Чтобы сделки попадали в воронку "зачислен",
        # надо будет просто ниже его поставить
        'Сформирован': 0,
        'Согласие На Зачисление': 1,
        'Подал Заявление': 2,
        'Зачислен': 3,
    }

    deals = await amo.get_all_deals()
    # print(len(deals))
    for deal in deals:
        lowest_status = 9999
        async for application in db.get(applicant_id=deal.applicant_id):
            contract_order = order_map.get(application.contract_status, 999)
            status_order = order_map.get(application.current_status, 999)
            if contract_order < status_order:
                if contract_order < lowest_status:
                    lowest_status = contract_order

            if status_order < contract_order:
                if status_order < lowest_status:
                    lowest_status = status_order

        status_id = status_map.get(lowest_status)
        if status_id is None:
            # print(f"\n\n{status_map.get(lowest_status)=}\n{lowest_status=}\n")
            # print(f'process_pipeline_statuses: cant obtain status_id. {deal=}')
            continue

        await amo.patch_deal_status(deal_id=deal.id, status_id=status_id)

