import asyncio
from aiohttp.client_exceptions import ServerDisconnectedError
from amo_crm.api import AmoCrmApi
from amo_crm.enums import CreationResultsEnum
from amo_crm.models import Deal
from database.deals_crud import DealsCRUD
from datetime import datetime


async def safe_create_deal(deal: Deal) -> tuple[bool, int]:
    amo = AmoCrmApi()
    await asyncio.sleep(1)

    try:
        result = await amo.create_deal(deal)
        assert isinstance(result, (int, float)), 'ERROR: RESULT IS NEITHER INT NOR FLOAT'

        if result == CreationResultsEnum.DUPLICATE:
            await amo.patch_deal(deal=deal)

        # Если всё норм, возвращаем кортеж
        return True, result if isinstance(result, int) else (False, result)

    except ServerDisconnectedError as e:
        print(f"WARNING: {e}. WAITING 2 SECS BEFORE TRYING TO UPLOAD {deal=}")
        await asyncio.sleep(2)
        return await safe_create_deal(deal=deal)


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
    async for deal in db.get():
        i += 1

        if any([is_updated(deal=deal), is_new(deal=deal)]):
            status, id_ = await safe_create_deal(deal=deal)

            if status is not True:
                print(f'ERROR: Status failed. {status=}, {id_=}, {deal=}')
                continue

            if isinstance(id_, int):
                await db.actualize_uploaded_at(deal=deal, crm_id=id_)
            else:
                await db.actualize_uploaded_at(deal=deal)

        else:
            print(f'INFO: Deal exists and is up to date. {i=}, {deal=}')
            continue

        print(
            f"RUN_DEALS: {i=}, AmoCrmEntityId={id_}, {is_new(deal)=},  "
            f"{is_updated(deal)=}, Deal={deal.dict()}"
        )
