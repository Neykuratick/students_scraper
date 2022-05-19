from config import settings
from aiohttp_requests import requests


async def _get_token(payload: dict) -> str:
    url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru/oauth2/access_token'
    response = await requests.post(url, json=payload)
    data = await response.json()

    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')

    if refresh_token is not None:
        with open('test.txt', 'w') as f:
            f.write(refresh_token)

    if not access_token:
        raise RuntimeError('Access token token is None')

    return 'Bearer ' + access_token


class TokenManager:
    token = None

    def __init__(self):
        pass

    async def get_token(self):
        if not self.token:
            await self.refresh_token()

        return self.token

    async def refresh_token(self):
        payload = {
            "client_id": settings.AMO_CLIENT_ID,
            "client_secret": settings.AMO_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": settings.AMO_REFRESH_TOKEN,
            "redirect_uri": settings.AMO_REDIRECT_URL,
        }

        self.token = await _get_token(payload)
