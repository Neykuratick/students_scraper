from amo_crm.models import Contact, PhoneNumberField, ValueField, EmailField, CompetitiveGroupField, Company, Deal
from amo_crm.token_manager import TokenManager
from config import settings
from aiohttp_requests import requests


class AmoCrmApi:
    def __init__(self):
        self.token_manager = TokenManager()

    async def _make_request_post(self, resource: str, payload: dict | list[dict]):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}?limit=1'
        headers = {'Authorization': await self.token_manager.get_token()}
        response = await requests.post(url, headers=headers, json=payload)
        return await response.json()

    async def _make_request_get(self, resource: str, payload: dict | list[dict]):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}?limit=1'
        headers = {'Authorization': await self.token_manager.get_token()}
        response = await requests.get(url, headers=headers, json=payload)
        return await response.json()

    async def _create(self, payload: list[dict], entity: str):
        data = await self._make_request_post(f'/api/v4/{entity}', payload=payload)

        try:
            return data.get('_embedded').get(entity)[0].get('id')
        except Exception as e:
            print(f'{entity.capitalize()} ERROR. Return data: {data}, Error: {e}')
            raise RuntimeError(f'Не удалось получить айди у {entity}')

    async def create_deal(self, deal: Deal) -> int:
        payload = [{
            'name': deal.contact.name,
            'pipeline_id': settings.AMO_PIPELINE_ID,
            '_embedded': {
                'contacts': [{'id': await self.create_contact(contact=deal.contact)}],
                'companies': [{'id': await self.create_company(company=deal.company)}],
            }
        }]

        return await self._create(payload=payload, entity='leads')

    async def create_company(self, company: Company):
        payload = [{
            'name': 'Название не указано',
            'custom_fields_values': [{
                'field_id': settings.AMO_FIELD_ID_WEBSITE,
                'values': [{'value': company.website}]
            }]
        }]

        return await self._create(payload=payload, entity='companies')

    async def create_contact(self, contact: Contact):
        phone_number = ValueField(value=contact.phone_number).dict()
        email = ValueField(value=contact.email).dict()
        competitive_group = ValueField(value=contact.competitive_group).dict()

        contact_payload = [
            {
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'custom_fields_values': [
                    PhoneNumberField(values=[phone_number]).dict(exclude_none=True),
                    EmailField(values=[email]).dict(exclude_none=True),
                    CompetitiveGroupField(values=[competitive_group]).dict(exclude_none=True)
                ]
            },
            {
                'name': contact.name
            }
        ]

        return await self._create(payload=contact_payload, entity='contacts')
