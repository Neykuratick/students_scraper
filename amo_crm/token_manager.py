from config import settings
from aiohttp_requests import requests


async def _get_token(payload: dict) -> str:
    url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru/oauth2/access_token'
    response = await requests.post(url, data=payload)
    data = await response.json()
    token = data.get('access_token')
    
    print(f"\n\n{token=}\n\n")
    
    if not token:
        raise RuntimeError('Refresh token is None')
    
    return token


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
        