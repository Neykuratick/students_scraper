import requests
from mpgu.captcha_resolver import login


class TokenManager:
    _cookie: str = None
    _csrf_token: str = None
    _headers: dict[str] = None

    def __init__(self):
        pass

    def validate_tokens(self):
        url = "https://dbs.mpgu.su/incoming_2021/jqgrid?action=request"

        payload = "_search=false" \
                  "&nd=1653831681755" \
                  "&rows=1" \
                  "&page=1" \
                  "&visibleColumns[]=id" \
                  "&visibleColumns[]=snils" \

        while True:
            response = requests.post(url, headers=self._headers, data=payload)
            if 'АИС ВУЗ - Вход' in response.text:
                print(f"MPGU TOKEN MANAGER: Didn't solve captcha")
                print(f"TOKEN MANAGER: {self._headers=}")
                self.refresh_token()
            else:
                break

    def get_token(self) -> str:
        self.validate_tokens()
        return self._csrf_token

    def get_cookie(self) -> str:
        self.validate_tokens()
        return self._cookie

    def get_headers(self) -> dict[str]:
        self.validate_tokens()
        return self._headers

    def refresh_token(self):
        details = login()
        self._cookie = details.cookie
        self._csrf_token = details.csrf_token
        self._headers = {
            'Cookie': details.cookie,
            'X-CSRF-Token': details.csrf_token,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }


token_manager = TokenManager()
