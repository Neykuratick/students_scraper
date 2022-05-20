from pydantic.env_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    AMO_CLIENT_SECRET: str
    AMO_CLIENT_ID: str
    AMO_SUBDOMAIN: str
    AMO_REDIRECT_URL: str
    AMO_AUTH_CODE: str
    AMO_REFRESH_TOKEN: str

    AMO_FIELD_ID_PHONE_NUMBER: int
    AMO_FIELD_ID_EMAIL: int
    AMO_FIELD_ID_COMPETITIVE_GROUP: int
    AMO_FIELD_ID_WEBSITE: int
    AMO_PIPELINE_ID: int

    # AMO_ENUM_ID_PHONE_NUMBER: int
    # AMO_ENUM_ID_EMAIL: int
    # AMO_ENUM_ID_COMPETITIVE_GROUP: int

    TEMP_COOKIE: str
    TEMP_MPGU_TOKEN: str


settings = Settings()

