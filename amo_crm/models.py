from enum import Enum
from pydantic import BaseModel, Field
from config import settings


class Finances(str, Enum):
    budget = "Бюджет"
    contract = "Договор"
    budget_contract = "Бюджет и Договор"


class ValueField(BaseModel):
    value: str
    enum_id: int | None
    enum_code: str | None


class PhoneNumberField(BaseModel):
    field_id: int = Field(settings.AMO_FIELD_ID_PHONE_NUMBER)
    # field_name: str = Field('Телефон')
    # field_code: str = Field('PHONE')
    # field_type: str = Field('multitext')
    values: list[ValueField]


class EmailField(BaseModel):
    field_id: int = Field(settings.AMO_FIELD_ID_EMAIL)
    # field_name: str = Field('Email')
    # field_code: str = Field('EMAIL')
    # field_type: str = Field('multitext')
    values: list[ValueField]


class CompetitiveGroupField(BaseModel):
    field_id: int = Field(settings.AMO_FIELD_ID_COMPETITIVE_GROUP)
    # field_name: str = Field('Программа1')
    # field_code: str = Field('None')
    # field_type: str = Field('multitext')
    values: list[ValueField]


class Contact(BaseModel):
    name: str
    first_name: str
    last_name: str
    phone_number: str
    email: str
    competitive_group: str


class Company(BaseModel):
    website: str


class Deal(BaseModel):
    applicant_id: int  # Айди абитуриента
    application_id: int  # Айди заявления в вуз
    contact: Contact
    company: Company
