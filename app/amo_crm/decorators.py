import asyncio
from aiohttp.client_exceptions import ServerDisconnectedError


def safe_http_request(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ServerDisconnectedError as e:
            print(f"WARNING: {e}. WAITING 2 SECS BEFORE TRYING TO UPLOAD {kwargs.get('payload')=}")
            await asyncio.sleep(2)
            return await func(*args, **kwargs)

    return wrapper
