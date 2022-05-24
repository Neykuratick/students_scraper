import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.deals_crud import DealsCRUD
from jobs.mpgu import store_deals


# db = DealsCRUD()
#
# if __name__ == '__main__':
#     scheduler = AsyncIOScheduler(timezone='UTC', daemon=True)
#     scheduler.add_job(store_deals, 'interval', [db], seconds=3)
#     scheduler.start()
#
#     asyncio.get_event_loop().run_forever()

async def main():
    db = DealsCRUD()
    print(await db.get_one('applicant_id', 547))
    async for doc in db.get():
        print(doc)


asyncio.run(main())
