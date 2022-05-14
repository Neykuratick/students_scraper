import requests

LOGIN_URL = 'https://dbs.mpgu.su/user/login'
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

response = requests.get(LOGIN_URL, headers=headers, verify=False)

headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
headers['content-type'] = 'application/x-www-form-urlencoded'
payload = {
    'username': '11',
    'password': '111'
}

response = requests.post(LOGIN_URL, data=payload, headers=headers, verify=False)
headers['cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
print(response.text)
