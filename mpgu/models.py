from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import validator
from pydantic.fields import Field


majors_map = {
    'АИФ': 50,
    'АЭК': 51,
    'АИТ': 52,
    'АМК': 1877,
    'ЖУР': 1822,
}


class Applicant(BaseModel):
    class Config:
        allow_population_by_field_name = True

    id: int
    incoming_id: int  # id абитуриента
    fullNameGrid: str
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    application_code: str
    competitiveGroup_name: str = Field(..., alias="competitiveGroup.name")
    application_number: str
    current_status: str = Field(..., alias="current_status_id")
    incoming_email: str = Field(..., alias="incoming.email")
    incoming_phone_mobile: str = Field(..., alias="incoming.phone_mobile")
    competitiveGroup_financing_type: str = Field(..., alias="competitiveGroup.financing_type_id")
    web_url: Optional[str] = Field(None)
    snils: Optional[str] = Field(None)

    @validator("first_name", always=True)
    def validate_first_name(cls, v, values):
        full_name = values.get('fullNameGrid')
        names = full_name.split(' ')

        if len(names) > 1:
            return full_name.split(' ')[0]
        else:
            return full_name

    @validator("last_name", pre=True, always=True)
    def validate_last_name(cls, v, values):
        full_name = values.get('fullNameGrid')
        names = full_name.split(' ')

        if len(names) > 2:
            return f'{names[1]} {names[2]}'
        elif len(names) > 1:
            return names[1]
        else:
            return ""

    @validator("web_url", pre=True, always=True)
    def validate_web_url(cls, v, values):
        url = "https://fok.sdo.mpgu.org/data-entrant/statement/view?id=" + str(values.get('incoming_id'))
        return url

    @validator("fullNameGrid", pre=True, always=True)
    def remove_first_end_spaces(cls, v):
        return "".join(v.rstrip().lstrip())

    @validator("current_status", pre=True, always=True)
    def validate_current_status(cls, v):
        # чтобы найти новые статусы, надо в компасе отправить квери {'current_status': '1'} и менять цифру по очереди
        # Два главных статуса у каждого договора - Сформирован (это значит, что договор заключен) и Оплачен (видна
        # сумма оплаты).

        return {
            11: 'Зачислен',
            10: 'Согласие На Зачисление',
            7: 'Не зачислен',
            6: 'ПредЗачислен',
            4: 'Забрал Заявление',
            3: 'Подал Заявление',
            1: 'Формируется',
        }.get(v, str(v))

    @validator("competitiveGroup_financing_type", pre=True, always=True)
    def validate_competitive_group_financing_type(cls, v):
        return {
            1: 'Бюджет',
            2: 'Договор',
        }.get(v, str(v))

    @validator("competitiveGroup_name", pre=True, always=True)
    def validate_competitive_group_name(cls, v):
        mapper = {
            "Бак | ИН | ИМО | ЖУР | межд жур | о |": "ЖУР (Иностр)",
            "Бак | ИМО | ЖУР | межд жур | о |": "ЖУР",
            "Бак | ИМО | ЛИНГ | англ яз и муждународ коммуник | о |": "АМК",
            "Бак | ИМО | МЕН | упр биз | о |": "МЕН",
            "Бак | ИМО | ПО2 | англ яз и франц яз | о |": "АИФ",
            "Бак | ИМО | ПО2 | иняз (англ) и инф тех в обр | о |": "АИТ",
            "Бак | ИМО | ПО2 | иняз (англ) и экон | о |": "АЭК",
            "Бак | ИМО | СИСТ | гейм диз и вр | о |": "ГДЗ",
            "Бак | ИМО | СИСТ | комп науки | о |": "КМП",
            "Бак | ИМО | СИСТ | раз моб и веб прил | о |": "РМП",
            "Маг | ИМО | ЛИНГ | междунар комм эк и биз | о |": "МЭК",
            "Маг | ИМО | ЛИНГ | межд ком в сф бизн и менед англ | о |": "МЭК",
            "Маг | ИМО | ПО | инн пред в эдтех | з |": "ЭДТ",
            "Маг | ИМО | ПО | проект обр опыта | з |": "ПРО",
            "Маг | ИМО | ПО | проект обр опыта совр обуч | з |": "ПРО",
            "Маг | ИМО | ПО | совр техно препод англ яз | з |": "СТЗ",
            "Маг | ИМО | ПО | совр техно препод англ яз (на англ яз) | з |": "СТЗ",
            "Маг | ИМО | ПО | совр техно препод англ яз | о |": "СТО",
            "Маг | ИМО | ПО | совр техно препод англ яз (на англ яз) | о |": "СТО",
            "Маг | ИН | ИМО | ПО | совр техно препод англ яз (на англ яз) | з | д": "СТЗ (Иностр)",
        }

        for key, value in mapper.items():
            if key in v:
                return value

        return v
