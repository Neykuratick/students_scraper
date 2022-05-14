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
    incoming_id: int
    vi_status: int
    current_status: str = Field(..., alias="current_status_id")
    incoming_incoming_type_id: int = Field(..., alias="incoming.incoming_type_id")
    competitiveGroup_education_level_id: int = Field(..., alias="competitiveGroup.education_level_id")
    fok_status: int

    @validator("fullNameGrid", pre=True, always=True)
    def remove_first_end_spaces(cls, v):
        return "".join(v.rstrip().lstrip())

    @validator("current_status", pre=True, always=True)
    def validate_current_status(cls, v):
        mapper = {
            11: 'Зачислен',
            10: 'Согласие На Зачисление',
            4: 'Забрал Заявление',
            3: 'Подал Заявление',
            1: 'Формируется',
        }

        # чтобы найти новые статусы, надо в компасе отправить квери {'current_status': '1'} и менять цифру по очереди

        return mapper.get(v, str(v))
