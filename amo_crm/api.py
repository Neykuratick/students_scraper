from amo_crm.token_manager import TokenManager
from config import settings
from aiohttp_requests import requests


class AmoCrmApi:
    def __init__(self):
        self.token_manager = TokenManager()

    async def make_request(self, resource: str, **kwargs):
        # url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}'
        url = "https://avkuznetsovmpgusu.amocrm.ru/api/v4/account"
        payload = None

        headers = {
            'Authorization: Bearer ': await self.token_manager.get_token(),
        }

        response = await requests.get(url, headers=headers)
        print(f"\n\n{response.text=}\n\n")
        data = await response.json()
        print(data)
