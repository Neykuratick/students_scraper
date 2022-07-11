from app.amo_crm.exceptions import InvalidAccessToken
from app.amo_crm.exceptions import InvalidRefreshToken
from app.database.deals_crud import db
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


class Token:
    def __init__(self, token: str, header: str, refresh_token: str):
        self.token = token
        self.header = header
        self.refresh_token = refresh_token


async def _get_token(payload: dict) -> Token:
    url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru/oauth2/access_token'
    response = await requests.post(url, json=payload)
    data = await response.json()

    access_token = data.get('access_token')
    refresh_token = data.get('refresh_token')

    if refresh_token is not None:
        with open('test.txt', 'w') as f:
            f.write(refresh_token)

    if not access_token:
        raise InvalidAccessToken(f'Access token token is None. {data=}')

    if not refresh_token:
        raise InvalidRefreshToken(f'CRITICAL!!!!!! REFRESH TOKEN IS NONE')

    return Token(token=access_token, header='Bearer ' + access_token, refresh_token=refresh_token)


class TokenManager:
    token: Token = None
    requests = 0

    def __init__(self):
        pass

    async def get_token(self) -> Token:
        if not self.token:
            await self.refresh_token()

        elif self.requests >= 100:
            await self.refresh_token()
            self.requests = 0

        self.requests += 1
        return self.token

    async def refresh_token(self):
        with open('test.txt', 'r') as f:
            refresh_token = f.read()

        payload = {
            "client_id": settings.AMO_CLIENT_ID,
            "client_secret": settings.AMO_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "redirect_uri": settings.AMO_REDIRECT_URL,
        }

        try:
            self.token = await _get_token(payload)
        except InvalidAccessToken as e:
            print(f'TokenManager Warning: {e=}')
            authorize_app()
            return await self.refresh_token()

        with open('test.txt', 'w') as f:
            print(f'TokenManager Info: updating {refresh_token=}')
            f.write(self.token.refresh_token)
            await db.insert_token(token=self.token.refresh_token)


token_manager = TokenManager()
