from database.deals_crud import DealsCRUD
from mpgu.api import get_latest_deals
from deepdiff import DeepDiff


async def actualize(deals_crud: DealsCRUD):
    async for new_deal in get_latest_deals():
        old_deal = await deals_crud.get_one('application_id', new_deal.application_id)

        diff = DeepDiff(new_deal.dict(), old_deal.dict())
        if not diff:
            continue

        # Если абитуриент поменялся, обновляем его заявку целиком
        await deals_crud.update_one(new_deal)
