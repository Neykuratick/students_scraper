from amo_crm.enums import CreationResultsEnum
from amo_crm.models import Contact, PhoneNumberField, ValueField, EmailField, CompetitiveGroupField, Company, Deal
from amo_crm.token_manager import TokenManager
from config import settings
from aiohttp_requests import requests


def compose_tag(deal: Deal) -> str:
    return f"Интеграционный номер {deal.applicant_id}"


class AmoCrmApi:
    def __init__(self):
        self.token_manager = TokenManager()

    @staticmethod
    def _process_response(status_code: int, url: str, response):
        assert status_code != 404, f'ERROR 404: RESOURCE NOT FOUND. {url=}, {response.text=}'
        assert status_code != 402, f'PAYMENT MIGHT BE REQUIRED, {url=}, {response.text=}'

    async def _make_request_patch(self, resource: str, payload: dict | list[dict]):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}'

        headers = {'Authorization': await self.token_manager.get_token()}
        response = await requests.patch(url, headers=headers, json=payload)
        self._process_response(status_code=response.status, url=url, response=response)

        return await response.json()

    async def _make_request_post(self, resource: str, payload: dict | list[dict]):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}?limit=1'

        headers = {'Authorization': await self.token_manager.get_token()}
        response = await requests.post(url, headers=headers, json=payload)
        self._process_response(status_code=response.status, url=url, response=response)

        return await response.json()

    async def _make_request_get(self, resource: str, payload: dict | list[dict], no_limit: bool = False):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}'
        url += '?limit=1' if not no_limit else ""

        headers = {'Authorization': await self.token_manager.get_token()}
        response = await requests.get(url, headers=headers, json=payload)
        self._process_response(status_code=response.status, url=url, response=response)

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

    async def _deal_exists(self, deal: Deal, searching_tag: str) -> bool:
        deals_ids = await self._find_deal(deal=deal)

        exists_by_crm_id = await self._crm_id_exists(deal=deal, searching_tag=searching_tag)
        exists_by_tag = await self._tag_exists(tag=searching_tag)
        exists_by_field_query = len(deals_ids) >= 1

        if any([exists_by_crm_id, exists_by_tag, exists_by_field_query]):
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

    async def _create_company(self, company: Company):
        payload = [{
            'name': 'Название не указано',
            'custom_fields_values': [{
                'field_id': settings.AMO_FIELD_ID_WEBSITE,
                'values': [{'value': company.website}]
            }]
        }]

        return await self._create(payload=payload, entity='companies')

    async def _create_contact(self, contact: Contact):
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

    async def _find_contract_id_by_deal_id(self, deal_id: int) -> int | None:
        data = await self._make_request_get(f'/api/v4/leads/{deal_id}/links', {}, no_limit=True)

        try:
            links = data.get('_embedded').get('links')

            for link in links:
                if link.get('to_entity_type') == 'contacts':
                    contact_id = link.get('to_entity_id')
                    return contact_id if isinstance(contact_id, int) else None

        except any([AttributeError, TypeError]):
            print(f'FIND CONTACT ERROR: contract data is presumably None. {data=}, {deal_id=}')
            return

    async def _find_deal(self, deal: Deal, patching: bool = None) -> list[int]:
        tag = compose_tag(deal=deal)
        data = await self._make_request_get(f'/api/v4/leads?query={tag} {deal.contact.name}', {}, no_limit=True)
        
        if data is None:
            # TODO Убрать из квери выше {deal.contact.name} и оставить только тег, если будет плохо искать
            print(f'CRITICAL ERROR: NO ONE FOUND!!!! {tag=}, {deal=}') if patching else None
            return []

        try:
            deals = data.get('_embedded').get('leads')
        except AttributeError:
            print(f'FIND DEAL ERROR: data deals is presumably None. {data=}, {deal=}')
            return []

        contact_ids = []

        for result_deal in deals:
            if result_deal.get('name') == deal.contact.name:
                deal_id = result_deal.get('id')
                print(f"DEBUG: Obtaining contacts for deal: {deal_id}")
                contact_id = await self._find_contract_id_by_deal_id(deal_id=deal_id)

                if isinstance(contact_id, int):
                    contact_ids.append(contact_id)
                else:
                    print(f'ERROR: Failed to find contact_id ({contact_id=}) for {deal=}')
            else:
                print(
                    f'WARNING: Queried {result_deal.get("name")}, '
                    f'while searching for {deal.contact.name} '
                    f'with {tag=}'
                )

        return contact_ids

    async def create_deal(self, deal: Deal) -> int | float:
        tag = compose_tag(deal=deal)
        deal_exists = await self._deal_exists(deal=deal, searching_tag=tag)

        if deal_exists is True:
            return CreationResultsEnum.DUPLICATE

        payload = [{
            'name': deal.contact.name,
            'pipeline_id': settings.AMO_PIPELINE_ID,
            '_embedded': {
                'contacts': [{'id': await self._create_contact(contact=deal.contact)}],
                'companies': [{'id': await self._create_company(company=deal.company)}],
                'tags': [{'name': tag}]
            }
        }]

        return await self._create(payload=payload, entity='leads')

    async def patch_deal(self, deal: Deal, new_competitive_group: str):
        contact_ids = await self._find_deal(deal=deal, patching=True)

        for contact_id in contact_ids:
            competitive_group = ValueField(value=new_competitive_group).dict()

            payload = {
                'custom_fields_values': [
                    CompetitiveGroupField(values=[competitive_group]).dict(exclude_none=True)
                ]

            }

            result = await self._make_request_patch(f'/api/v4/contacts/{contact_id}', payload)
            print(f"\n\n{result=}\n\n")

        # TODO: OPTIMIZE CONTACT_ID SEARCH.
        print(f'DEBUG: PATCHING. {contact_ids=}')
