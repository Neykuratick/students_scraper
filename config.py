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


settings = Settings()
