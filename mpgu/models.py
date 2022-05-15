from pydantic import BaseModel
from pydantic.class_validators import validator
from pydantic.fields import Field


class Applicant(BaseModel):
    class Config:
        allow_population_by_field_name = True

    id: int
    fullNameGrid: str
    application_code: str
    competitiveGroup_name: str = Field(..., alias="competitiveGroup.name")
    application_number: str
    current_status: str = Field(..., alias="current_status_id")
    incoming_email: str = Field(..., alias="incoming.email")
    incoming_phone_mobile: str = Field(..., alias="incoming.phone_mobile")
    competitiveGroup_financing_type: str = Field(..., alias="competitiveGroup.financing_type_id")
    incoming_id: int  # id абитуриента

    @validator("fullNameGrid", pre=True, always=True)
    def remove_first_end_spaces(cls, v):
        return "".join(v.rstrip().lstrip())

    @validator("current_status", pre=True, always=True)
    def validate_current_status(cls, v):
        # чтобы найти новые статусы, надо в компасе отправить квери {'current_status': '1'} и менять цифру по очереди

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
            "Маг | ИМО | ПО | инн пред в эдтех | з |": "ЭДТ",
            "Маг | ИМО | ПО | проект обр опыта | з |": "ПРО",
            "Маг | ИМО | ПО | совр техно препод англ яз | з |": "СТЗ",
            "Маг | ИМО | ПО | совр техно препод англ яз | о |": "СТО",
        }

        for key, value in mapper.items():
            if key in v:
                return value

        return v

