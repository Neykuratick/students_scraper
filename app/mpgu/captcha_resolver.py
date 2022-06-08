import base64
import requests
from pydantic.main import BaseModel
from requests import Session
from bs4 import BeautifulSoup
from config import settings
from time import sleep


class LoginDetails(BaseModel):
    cookie: str
    csrf_token: str


class Resolver:

    def __init__(self, session: Session):
        self.session = session
        self.csrf_token = None

    def _set_token(self, soup: BeautifulSoup):
        csrf_token_div = soup.find("meta", {"name": "csrf-token"})
        csrf_token = csrf_token_div['content']
        self.csrf_token = csrf_token

    def _get_image(self, session: Session) -> bytes:
        r = session.get('https://dbs.mpgu.su/user/login')
        soup = BeautifulSoup(r.text, 'html.parser')
        self._set_token(soup=soup)

        img = soup.find('img', id='loginform-verifycode-image')
        image_endpoint = img['src']
        image_url = settings.MPGU_BASE_URL + image_endpoint

        r = session.get(image_url)
        return base64.b64encode(r.content)

    def _get_captcha(self, id_: int, session: Session):
        payload = (
                f'?key={settings.RUCAPTCHA_KEY}' +
                '&action=get' +
                f'&id={id_}' +
                f'&json=1'
        )
        r = session.get(f'https://rucaptcha.com/res.php' + payload)
        response = r.json().get('request')

        if response == 'CAPCHA_NOT_READY':
            print(f'CAPTCHA: Captcha is not ready')
            sleep(5)
            return self._get_captcha(id_=id_, session=session)
        elif response == 'ERROR_CAPTCHA_UNSOLVABLE':
            return None

        if isinstance(response, str):
            return response

        print(f'CAPTCHA: final {response=}')

    def resolve_captcha(self) -> str:
        json = {
            'key': settings.RUCAPTCHA_KEY,
            'method': 'base64',
            'body': self._get_image(session=self.session),
            'json': 1,
        }
        r = self.session.post('https://rucaptcha.com/in.php', json)
        captcha_id = r.json().get('request')
        captcha_value = self._get_captcha(id_=captcha_id, session=self.session)
        return captcha_value


def login() -> LoginDetails:
    resolver = Resolver(requests.Session())

    captcha_value = resolver.resolve_captcha()
    csrf_token = resolver.csrf_token

    _csrf_old = resolver.session.cookies.get('_csrf')
    phpsessid_old = resolver.session.cookies.get('PHPSESSID')
    cookie_old = f"PHPSESSID={phpsessid_old}; _csrf={_csrf_old}"

    headers = {
        'Cookie': cookie_old,
        'X-CSRF-Token': csrf_token,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = f'_csrf={csrf_token}' \
              f'&LoginForm[usr]={settings.MPGU_LOGIN}' \
              f'&LoginForm[password]={settings.MPGU_PASSWORD}' \
              f'&LoginForm[verifyCode]={captcha_value}' \
              '&login-button='

    resolver.session.post("https://dbs.mpgu.su/user/login", data=payload, headers=headers)
    r = resolver.session.get('https://dbs.mpgu.su/incoming_2022/application')

    _csrf = resolver.session.cookies.get('_csrf')
    phpsessid = resolver.session.cookies.get('PHPSESSID')
    cookie = f'PHPSESSID={phpsessid}; _csrf={_csrf}'

    soup = BeautifulSoup(r.text, 'html.parser')
    csrf_token_div = soup.find("meta", {"name": "csrf-token"})
    csrf_token = csrf_token_div['content']

    return LoginDetails(cookie=cookie, csrf_token=csrf_token)
