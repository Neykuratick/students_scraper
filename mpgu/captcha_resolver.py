import base64
import requests
from requests import Session
from bs4 import BeautifulSoup
from config import settings, mpgu_headers
import time


def _get_csrf_token(session: Session) -> str:
    r = session.get('https://dbs.mpgu.su/user/login')
    soup = BeautifulSoup(r.text, 'html.parser')

    csrf_token_div = soup.find("meta", {"name": "csrf-token"})
    csrf_token = csrf_token_div['content']
    return csrf_token


def _get_image(session: Session) -> bytes:
    r = session.get('https://dbs.mpgu.su/user/login')
    soup = BeautifulSoup(r.text, 'html.parser')

    img = soup.find('img', id='loginform-verifycode-image')
    image_endpoint = img['src']

    image_url = settings.MPGU_BASE_URL + image_endpoint

    r = session.get(image_url)
    encoded_string = base64.b64encode(r.content)

    return encoded_string


def _get_captcha(id_: int, session: Session):
    payload = (
            f'?key={settings.RUCAPTCHA_KEY}' +
            '&action=get' +
            f'&id={id_}' +
            f'&json=1'
    )
    r = session.get(f'https://rucaptcha.com/res.php' + payload)
    response = r.json().get('request')

    if response == 'CAPTCHA_NOT_READY':
        print(f'CAPTCHA: Captcha is not ready')
        time.sleep(5)
        return _get_captcha(id_=id_, session=session)
    elif response == 'ERROR_CAPTCHA_UNSOLVABLE':
        return None

    if isinstance(response, str):
        return response

    print(f'CAPTCHA: final {response=}')


def _resolve_captcha(session: Session) -> str:
    json = {
        'key': settings.RUCAPTCHA_KEY,
        'method': 'base64',
        'body': _get_image(session=session),
        'json': 1,
    }
    r = session.post('https://rucaptcha.com/in.php', json)
    captcha_id = r.json().get('request')
    captcha_value = _get_captcha(id_=captcha_id, session=session)
    return captcha_value


def set_tokens():
    session = requests.Session()
    captcha_value = _resolve_captcha(session=session)
    csrf_token = _get_csrf_token(session=session)

    _csrf = session.cookies.get('_csrf')
    phpsessid = session.cookies.get('PHPSESSID')
    cookie = f'PHPSESSID={phpsessid}; _csrf={_csrf}'

    headers = {
        'Cookie': cookie,
        'X-CSRF-Token': csrf_token,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = f'_csrf={csrf_token}' \
              f'&LoginForm[usr]={settings.MPGU_LOGIN}' \
              f'&LoginForm[password]={settings.MPGU_PASSWORD}' \
              f'&LoginForm[verifyCode]={captcha_value}' \
              '&login-button='

    session.post("https://dbs.mpgu.su/user/login", data=payload, headers=headers)

    settings.TEMP_COOKIE = cookie
    settings.TEMP_MPGU_TOKEN = csrf_token
    mpgu_headers['Cookie'] = cookie
    mpgu_headers['X-CSRF-Token'] = csrf_token
