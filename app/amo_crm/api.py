from app.amo_crm.decorators import safe_http_request
from app.amo_crm.models import (
    Contact, PhoneNumberField, ValueField, EmailField,
    CompetitiveGroupField, Company, Deal,
)
from app.amo_crm.token_manager import TokenManager
from config import settings
from aiohttp_requests import requests


def compose_tag(deal: Deal) -> str:
    return f"Интеграционный номер {deal.applicant_id}"


def get_company_payload(company: Company):
    payload = [{
        'name': 'Название не указано',
        'custom_fields_values': [{
            'field_id': settings.AMO_FIELD_ID_WEBSITE,
            'values': [{'value': company.website}]
        }]
    }]

    return payload


def get_contact_payload(contact: Contact):
    phone_number = ValueField(value=contact.phone_number).dict()
    email = ValueField(value=contact.email).dict()
    competitive_group = ValueField(value=contact.competitive_group).dict()

    contact_payload = [
        {
            'name': contact.name,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'custom_fields_values': [
                PhoneNumberField(values=[phone_number]).dict(exclude_none=True),
                EmailField(values=[email]).dict(exclude_none=True),
                CompetitiveGroupField(values=[competitive_group]).dict(exclude_none=True)
            ]
        }
    ]

    return contact_payload


class AmoCrmApi:
    def __init__(self):
        self.token_manager = TokenManager()

    @staticmethod
    def _process_response(status_code: int, url: str, response):
        assert status_code != 404, f'ERROR 404: RESOURCE NOT FOUND. {url=}, {response.text=}'
        assert status_code != 402, f'PAYMENT MIGHT BE REQUIRED, {url=}, {response.text=}'

    @safe_http_request
    async def _make_request_patch(self, resource: str, payload: dict | list[dict]):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}'

        headers = {'Authorization': await self.token_manager.get_token()}
        response = await requests.patch(url, headers=headers, json=payload)
        self._process_response(status_code=response.status, url=url, response=response)

        return await response.json()

    @safe_http_request
    async def _make_request_post(self, resource: str, payload: dict | list[dict]):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}'

        headers = {'Authorization': await self.token_manager.get_token()}
        response = await requests.post(url, headers=headers, json=payload)
        self._process_response(status_code=response.status, url=url, response=response)

        return await response.json()

    @safe_http_request
    async def _make_request_get(
        self, resource: str, payload: dict | list[dict], no_limit: bool = False
        ):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}'
        url += '?limit=1' if not no_limit else ""

        headers = {'Authorization': await self.token_manager.get_token()}
        response = await requests.get(url, headers=headers, json=payload)
        self._process_response(status_code=response.status, url=url, response=response)

        if response.status == 204:
            return None

        return await response.json()

    async def _find_deal(self, deal: Deal, patching: bool = None) -> list[int | dict]:
        """ Возвращает либо сделки, либо айди контактов всех дубликатов этой сделки """
        tag = compose_tag(deal=deal)
        url = f'/api/v4/leads?query={tag} {deal.contact.name}'
        data = await self._make_request_get(url, {}, no_limit=True)

        if data is None:
            # TODO Убрать из квери выше {deal.contact.name} и оставить только тег, если будет
            #  плохо искать
            print(f'CRITICAL ERROR: NO ONE FOUND!!!! {tag=}, {deal=}') if patching else None
            return []

        try:
            deals = data.get('_embedded').get('leads')
        except AttributeError:
            print(f'FIND DEAL ERROR: data deals is presumably None. {data=}, {deal=}')
            return []

        if patching:
            return await self.find_contract_by_deal_duplicates(
                original_deal=deal, duplicate_deals=deals
                )
        else:
            return deals

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

    async def _find_deals_by_tag(self, tag: str, searching_deal: Deal) -> bool:
        """ По сути, не находит сделки, а проверяет, есть ли по такому тегу или нет """
        data = await self._make_request_get(
            f'/api/v4/leads?query={tag}', {}, no_limit=True
        )

        try:
            deal = data.get('_embedded').get('leads')[0]
            return True if deal.get('name') == searching_deal.contact.name else False
        except:
            return False

    async def _tag_exists(self, tag: str, deal: Deal) -> bool:
        url = f'/api/v4/leads/tags?query={tag}'
        data = await self._make_request_get(url, payload={}, no_limit=True)

        if data is None:
            f'tag_exists returned None. {url=}'
            return False

        try:
            returned_tag = data.get('_embedded').get('tags')[0].get('name')
            print(f'WARNING: Tag is not instance of string. {data=}') if not isinstance(tag, str) else None
            if tag == returned_tag:
                return await self._find_deals_by_tag(tag=returned_tag, searching_deal=deal)
            else:
                f'tag_exists {tag=} is not equeals {returned_tag=}'
                return False

        except any([AttributeError, IndexError]) as e:
            print(f'tag_exists. Caught {e=}')
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
        exists_by_tag = await self._tag_exists(tag=searching_tag, deal=deal)
        exists_by_field_query = len(deals_ids) >= 1

        print(f'DEAL EXISTS? applicant_id={deal.applicant_id}, {exists_by_crm_id=}, {exists_by_tag=} {exists_by_field_query=}')

        if any([exists_by_crm_id, exists_by_tag, exists_by_field_query]):
            return True
        else:
            return False

    async def find_contract_by_deal_duplicates(
        self, original_deal: Deal, duplicate_deals: list[dict]
        ):
        contact_ids = []

        for index, result_deal in enumerate(duplicate_deals):
            if result_deal.get('name') != original_deal.contact.name:
                print(
                    f'WARNING: Queried {result_deal.get("name")}, '
                    f'while searching for {original_deal.contact.name} '
                    f'with tag={compose_tag(deal=original_deal)}'
                    )
                continue

            deal_id = result_deal.get('id')

            debug_data = f"{deal_id} ({original_deal.contact.name}). {index + 1}/" \
                         f"{len(duplicate_deals)}"
            print(f"DEBUG: Obtaining contacts for deal: {debug_data}")

            contact_id = await self._find_contract_id_by_deal_id(deal_id=deal_id)

            if contact_id is not None:
                contact_ids.append(contact_id)

        print(f"{len(duplicate_deals)=}, {len(contact_ids)=}")
        return contact_ids

    async def create_deal(self, deal: Deal) -> dict:
        tag = compose_tag(deal=deal)
        deal_exists = await self._deal_exists(deal=deal, searching_tag=tag)

        if deal_exists is True:
            return {'detail': 'duplicate'}

        payload = [{
            'name': deal.contact.name,
            'pipeline_id': settings.AMO_PIPELINE_ID,
            '_embedded': {
                'contacts': get_contact_payload(contact=deal.contact),
                'companies': get_company_payload(company=deal.company),
                'tags': [{'name': tag}]
            }
        }]

        print(f"\n\nCREATING DEAL!!!!!!!! {deal=}\n\n")
        data = await self._make_request_post(payload=payload, resource='/api/v4/leads/complex')
        
        try:
            new_deal_id = data[0].get('id')
        except:
            raise RuntimeError(f"Не удалось получить айди у сделки. {data=}")
        
        if isinstance(new_deal_id, int):
            return {'detail': 'success', 'deal_id': new_deal_id}
        else:
            print(f'ERROR. DEAL ID IS NOT INT. {new_deal_id=}')
            return {'detail': 'failed'}

    async def patch_deal(self, deal: Deal, new_competitive_group: str):
        contact_ids = await self._find_deal(deal=deal, patching=True)
        print(f'DEBUG: PATCHING. {contact_ids=}')

        patched_contacts = 0

        for index, contact_id in enumerate(contact_ids):
            competitive_group = ValueField(value=new_competitive_group).dict()

            payload = {
                'custom_fields_values': [
                    CompetitiveGroupField(values=[competitive_group]).dict(exclude_none=True)
                ]
            }

            result = await self._make_request_patch(f'/api/v4/contacts/{contact_id}', payload)
            print(
                f"({index + 1}/{len(contact_ids)}) PATCHED SUCCESSFULLY. NEW GROUPS: "
                f"{new_competitive_group}. NEW INSTANCE: {result=}"
                )
            # TODO SAFE CHECK. If contact was patched successfully, +1. Else - no +1
            patched_contacts += 1

        if patched_contacts > 0:
            return {'detail': 'success', 'deal_id': deal.crm_id}
