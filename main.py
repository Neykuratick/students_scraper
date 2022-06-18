import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.amo_crm.job import process_pipeline_statuses
from app.amo_crm.job import run_deals
from app.mpgu.job import store_deals, actualize_contracts

scheduler = AsyncIOScheduler(timezone='UTC', daemon=True)
scheduler.add_job(actualize_contracts, 'interval', seconds=3)
scheduler.add_job(store_deals, 'interval', seconds=3)
scheduler.add_job(run_deals, 'interval', seconds=3)
scheduler.add_job(process_pipeline_statuses, 'interval', seconds=3)
scheduler.start()

asyncio.get_event_loop().run_forever()



