import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.deals_crud import db
from amo_crm.job import run_deals
from mpgu.job import store_deals, actualize_contracts

scheduler = AsyncIOScheduler(timezone='UTC', daemon=True)
scheduler.add_job(actualize_contracts, 'interval', seconds=3)
scheduler.add_job(store_deals, 'interval', seconds=3)
# scheduler.add_job(run_deals, 'interval', [db], seconds=3)
scheduler.start()

asyncio.get_event_loop().run_forever()


# async def main():
#     import datetime
#     print(datetime.datetime.now())
#     await actualize_contracts()
#     print(datetime.datetime.now())
#
# asyncio.run(main())

# TODO admin report message
# TODO move student's card in the AMOCRM pipeline according to the current application status


