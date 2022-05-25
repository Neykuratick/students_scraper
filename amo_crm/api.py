from amo_crm.enums import CreationResultsEnum
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

    async def _make_request_get(self, resource: str, payload: dict | list[dict], no_limit: bool = False):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}'
        url += '?limit=1' if not no_limit else ""

        headers = {'Authorization': await self.token_manager.get_token()}
        response = await requests.get(url, headers=headers, json=payload)

        if response.status == 204:
            return None

        return await response.json()

    async def _tag_exists(self, tag: str) -> bool:
        data = await self._make_request_get(f'/api/v4/leads/tags?query={tag}', payload={}, no_limit=True)

        if data is None:
            return False

        try:
            returned_tag = data.get('_embedded').get('tags')[0].get('name')
            print(f'WARNING: Tag is not instance of string. {data=}') if not isinstance(tag, str) else None
            return True if tag == returned_tag else False

        except any([AttributeError, IndexError]):
            return False

    async def _crm_id_exists(self, deal: Deal, searching_tag: str) -> bool:
        if not isinstance(deal.crm_id, int):
            return False

        data = await self._make_request_get(f'/api/v4/leads/{deal.crm_id}', {})

        try:
            tag = data.get('_embedded').get('tags')[0].get('name')
            if isinstance(tag, str):
                return True if searching_tag == tag else False

            print(f'WARNING: Tag is not instance of string. {data=}')
            return False

        except any([AttributeError, IndexError]):
            return False

    async def _deal_exists(self, deal: Deal, searching_tag: str):
        exists_by_crm_id = await self._crm_id_exists(deal=deal, searching_tag=searching_tag)
        exists_by_tag = await self._tag_exists(tag=searching_tag)
        # TODO: exists_by_field_query https://www.amocrm.ru/developers/content/crm_platform/contacts-api#contacts-list

        if any([exists_by_crm_id, exists_by_tag]):
            return True
        else:
            return False

    async def _create(self, payload: list[dict], entity: str):
        data = await self._make_request_post(f'/api/v4/{entity}', payload=payload)

        try:
            return data.get('_embedded').get(entity)[0].get('id')
        except Exception as e:
            print(f'ERROR: {entity.capitalize()}. Return data: {data}, Error: {e}')
            raise RuntimeError(f'Не удалось получить айди у {entity}')

    async def create_deal(self, deal: Deal) -> int | float:
        tag = f"Интеграционный номер {deal.applicant_id}"

        if await self._deal_exists(deal=deal, searching_tag=tag):
            return CreationResultsEnum.DUPLICATE

        payload = [{
            'name': deal.contact.name,
            'pipeline_id': settings.AMO_PIPELINE_ID,
            '_embedded': {
                'contacts': [{'id': await self.create_contact(contact=deal.contact)}],
                'companies': [{'id': await self.create_company(company=deal.company)}],
                'tags': [{'name': tag}]
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
