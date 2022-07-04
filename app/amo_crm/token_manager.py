from config import settings
from aiohttp_requests import requests
from requests import post


def authorize_app():
    """
        Если был утерян Refresh Token, надо поменять секретный ключ в интеграции, а потом вызвать
        эту функцию.
        Авторизовывать одно и то же приложение можно раз в 20 минут,
        иначе будет ошибка Authorization code has been revoked
    """
    payload = {
        "client_id": settings.AMO_CLIENT_ID,
        "client_secret": settings.AMO_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": settings.AMO_AUTH_CODE,
        "redirect_uri": settings.AMO_REDIRECT_URL,
    }

    url = f'https://avkuznetsovmpgusu.amocrm.ru/oauth2/access_token'
    response = post(url, json=payload)
    data = response.json()

    refresh_token = data.get('refresh_token')

    if refresh_token is not None:
        with open('test.txt', 'w') as f:
            f.write(refresh_token)
    else:
        print(f'Refresh roken is none: {data}')

    return data


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
        raise RuntimeError(f'Access token token is None. {data=}')

    if not refresh_token:
        raise RuntimeError(f'CRITICAL!!!!!! REFRESH TOKEN IS NONE')

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
        with open('test.txt', 'r') as f:
            refresh_token = f.read()

        if refresh_token is None:
            raise RuntimeError(f'CRITICAL!!!!!! REFRESH TOKEN IS NONE')

        payload = {
            "client_id": settings.AMO_CLIENT_ID,
            "client_secret": settings.AMO_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": settings.AMO_REDIRECT_URL,
        }

        self.token = await _get_token(payload)


token_manager = TokenManager()
