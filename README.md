## Стек
- Language: python
- Data validator: pydantic
- Database: mongodb
- Database orm: motor
- Asyncio: asyncio
- Captcha resolver: rucaptcha
- Telegram framework: aiogram

## Деплой

- `docker network create integrationbot`
- `docker-compose up --build`
- Ctrl+c
- `docker network connect integrationbot mongodb-mpgu`
- `docker network connect integrationbot integration`
- `docker network connect integrationbot applicants-bot`

- Копируем ip `docker network inspect -f '{{range.IPAM.Config}}{{.Gateway}}{{end}}' integrationbot`
- Вставляем в .env: `DB_HOST=скопированный айпи`
- `docker-compose up --build`