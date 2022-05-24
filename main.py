import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.deals_crud import DealsCRUD
from jobs.mpgu import store_deals


db = DealsCRUD()

if __name__ == '__main__':
    scheduler = AsyncIOScheduler(timezone='UTC', daemon=True)
    scheduler.add_job(store_deals, 'interval', [db], seconds=3)
    scheduler.start()

    asyncio.get_event_loop().run_forever()


# async def main():
#     await store_deals(db)
#
#
# asyncio.run(main())


"""
TODO
выяснить как реализовать поиск уже существующей сделки
искать по ссылке в компании. Там уникальный айди абитуриента содержится
добавлять программы через запятую в поле "программа1"
"""
