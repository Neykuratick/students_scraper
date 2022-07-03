from app.amo_crm.decorators import safe_http_request
from app.amo_crm.models import (
    Contact, PhoneNumberField, ValueField, EmailField,
    CompetitiveGroupField, Company, Deal,
)
from app.amo_crm.models import GetDeal
from app.amo_crm.token_manager import TokenManager
from app.amo_crm.token_manager import token_manager
from app.database.deals_crud import db
from config import settings
import requests


def strings_equal(original: str, compared: str):
    return original.lower().replace('ё', 'е') == compared.lower().replace('ё', 'е')


def compose_tag(deal: Deal) -> str:
    return f"Интеграционный номер {deal.applicant_id}"


def get_tag(lead: dict) -> str:
    tags = lead.get('_embedded').get('tags')
    for tag in tags:
        tag_name = tag.get('name')
        if 'Интеграционный' in tag_name:
            return tag_name


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
        self.statuses_blacklist = [40582729, 40582726, 40879399, 48720784]
        self.statuses_whitelist = [40586116, 40586119]

    @staticmethod
    def _process_response(status_code: int, url: str, response):
        assert status_code != 404, f'ERROR 404: RESOURCE NOT FOUND. {url=}, {response.text=}'
        assert status_code != 402, f'PAYMENT MIGHT BE REQUIRED, {url=}, {response.text=}'

    @safe_http_request
    async def _make_request_patch(self, resource: str, payload: dict | list[dict]):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}'

        headers = {'Authorization': await token_manager.get_token()}
        response = requests.patch(url, headers=headers, json=payload)
        self._process_response(status_code=response.status_code, url=url, response=response)

        return response.json()

    @safe_http_request
    async def _make_request_post(self, resource: str, payload: dict | list[dict]):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}'

        headers = {'Authorization': await token_manager.get_token()}
        response = requests.post(url, headers=headers, json=payload)
        self._process_response(status_code=response.status_code, url=url, response=response)

        return response.json()

    @safe_http_request
    async def _make_request_get(
        self, resource: str, payload: dict | list[dict], no_limit: bool = False
    ):
        url = f'https://{settings.AMO_SUBDOMAIN}.amocrm.ru{resource}'

        if no_limit is False:
            url += '?limit=1'

        headers = {'Authorization': await token_manager.get_token()}
        response = requests.get(url, headers=headers, json=payload)
        self._process_response(status_code=response.status_code, url=url, response=response)

        if response.status_code == 204:
            return None

        return response.json()

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
            return strings_equal(deal.get('name'), searching_deal.contact.name)
        except:
            return False

    async def _tag_exists(self, tag: str, deal: Deal) -> bool:
        url = f'/api/v4/leads/tags?query={tag}'
        data = await self._make_request_get(url, payload={}, no_limit=True)

        if data is None:
            f'tag_exists returned None. {url=}'
            return False

        try:
            returned_tag = get_tag(lead=data)
            print(f'WARNING: Tag is not instance of string. {data=}') if not isinstance(
                tag, str
            ) else None
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
            tag = get_tag(lead=data)
            if isinstance(tag, str):
                return True if searching_tag == tag else False

            print(f'WARNING: Tag is not instance of string. {data=}')
            return False

        except any([AttributeError, IndexError]):
            return False

    @staticmethod
    async def find_crm_id(deal: Deal) -> int:
        async for application in db.get(applicant_id=deal.applicant_id):
            if application.crm_id is not None:
                return application.crm_id

    async def _deal_exists(self, deal: Deal, searching_tag: str) -> bool:
        if isinstance(deal.crm_id, int):
            return True

        deals_ids = await self._find_deal(deal=deal)
        exists_by_crm_id = await self._crm_id_exists(deal=deal, searching_tag=searching_tag)
        exists_by_tag = await self._tag_exists(tag=searching_tag, deal=deal)
        exists_by_field_query = len(deals_ids) >= 1

        print(
            f'DEAL EXISTS? applicant_id={deal.applicant_id}, {exists_by_crm_id=}, '
            f'{exists_by_tag=} {exists_by_field_query=}'
        )

        if any([exists_by_crm_id, exists_by_tag, exists_by_field_query]):
            return True
        else:
            return False

    async def find_contract_by_deal_duplicates(
        self, original_deal: Deal, duplicate_deals: list[dict]
    ):
        contact_ids = []

        for index, result_deal in enumerate(duplicate_deals):
            if not strings_equal(result_deal.get('name'), original_deal.contact.name):
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

    async def patch_deal_status(self, deal_id: int, status_id: int):
        existing_deal = await self._make_request_get(
            resource=f'/api/v4/leads/{deal_id}',
            payload={}
        )

        existing_id = existing_deal.get('status_id')

        if existing_id in self.statuses_blacklist:
            # если сделка находится в человеческой колонке
            if status_id not in self.statuses_whitelist:
                # если новый статус не "подал согласие" или не "договор заключён"
                return

        if existing_id == status_id:
            return

        payload = [
            {
                "id": deal_id,
                "pipeline_id": settings.AMO_PIPELINE_ID,
                "status_id": status_id,
            }
        ]

        res = await self._make_request_patch(resource='/api/v4/leads', payload=payload)
        print(f'status_patching: {res=}')

    async def patch_deal(self, deal: Deal, new_competitive_group: str):
        deal_id = await self.find_crm_id(deal=deal)
        print(f'DEBUG: found local crm_id: {deal_id}')

        if deal_id is not None:
            contact_ids = [await self._find_contract_id_by_deal_id(deal_id=deal_id)]
            print(f'DEBUG: fround contact_id by local crm_id: {contact_ids=}')
        else:
            contact_ids = await self._find_deal(deal=deal, patching=True)
            print(f'DEBUG: fround contact_id by _find_deal crm_id: {contact_ids=}')

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
            contact_id_new = result.get('id')
            deal_result = await self._make_request_get(
                f'/api/v4/contacts/{contact_id_new}/links', {}
            )

            try:
                links = deal_result.get('_embedded').get('links')
                for link in links:
                    if link.get('to_entity_type') == 'leads':
                        deal_id = link.get('to_entity_id')
            except:
                print(f'ERROR Amocrm: cant get id. {deal_result=}')

            print(
                f"({index + 1}/{len(contact_ids)}) PATCHED SUCCESSFULLY. NEW GROUPS: "
                f"{new_competitive_group}. NEW INSTANCE: {result=}"
            )

            patched_contacts += 1

        print(f'DEBUG PATCHING. returning id: {deal.crm_id=}, {deal_id=}')
        if patched_contacts > 0:
            return {'detail': 'success', 'deal_id': deal.crm_id or deal_id}

    @staticmethod
    def compose_deal(data: dict) -> list[GetDeal]:
        leads = []

        try:
            api_leads = data.get('_embedded').get('leads')
        except Exception as e:
            print(f'\n\nget_all_deals: unable to process {data=}. Exception: {e}\n\n')
            return []

        for lead in api_leads:
            try:
                tag_name = get_tag(lead=lead)
                applicant_id = int(tag_name.split('Интеграционный номер ')[1])
                leads.append(GetDeal(**lead, applicant_id=applicant_id))
            except Exception as e:
                print(f'\n\nget_all_deals: unable to process {lead=}. Exception: {e}\n\n')

        return leads

    async def get_all_deals(self) -> list[GetDeal]:
        leads = []

        data = await self._make_request_get(
            resource='/api/v4/leads?limit=250', payload={}, no_limit=True
        )
        leads += AmoCrmApi.compose_deal(data=data)

        while data.get('_links').get('next') is not None:
            url = data.get('_links').get('next').get('href')
            resource = url.split('https://avkuznetsovmpgusu.amocrm.ru')[1]
            data = await self._make_request_get(resource=resource, payload={}, no_limit=True)
            leads += AmoCrmApi.compose_deal(data=data)

        return leads
