import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from amo_crm.api import AmoCrmApi
from amo_crm.models import Contact, Deal, Company
from database.deals_crud import DealsCRUD
from jobs.amocrm import run_deals
from jobs.mpgu import store_deals


db = DealsCRUD()

if __name__ == '__main__':
    scheduler = AsyncIOScheduler(timezone='UTC', daemon=True)
    # scheduler.add_job(store_deals, 'interval', [db], seconds=3)
    scheduler.add_job(run_deals, 'interval', [db], seconds=3)
    scheduler.start()

    asyncio.get_event_loop().run_forever()


# async def main():
#     pass
#
#
# asyncio.run(main())


"""
TODO
выяснить как реализовать поиск уже существующей сделки
искать по ссылке в компании. Там уникальный айди абитуриента содержится
добавлять программы через запятую в поле "программа1"
"""
