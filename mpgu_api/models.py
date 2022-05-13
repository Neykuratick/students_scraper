from pydantic import BaseModel
from pydantic.fields import Field


class Applicant(BaseModel):
    fullNameGrid: str
    application_code: str
    competitiveGroup_name: str = Field(..., alias="competitiveGroup.name")
    application_number: str
    incoming_id: int
    vi_status: int
    current_status_id: int
    incoming_incoming_type_id: int = Field(..., alias="incoming.incoming_type_id")
    competitiveGroup_education_level_id: int = Field(..., alias="competitiveGroup.education_level_id")
    fok_status: int
