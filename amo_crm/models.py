from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from config import settings
from datetime import  datetime


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
    updated_at: Optional[datetime] = Field(None)
    inserted_at: Optional[datetime] = Field(None)
    uploaded_at: Optional[datetime] = Field(None)
    crm_id: Optional[int] = Field(None)
    snils: Optional[str] = Field(None)
    contract_status: Optional[str] = Field(None)
    current_status: Optional[str] = Field(None)
    mpgu_contract_number: Optional[str] = Field(None)

    applicant_id: int  # id абитуриента
    application_id: int  # id заявления в вуз
    contact: Contact
    company: Company

    class Config:
        allow_population_by_field_name = True
