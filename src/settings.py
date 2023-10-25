import os

from pydantic import BaseSettings

class Settings(BaseSettings):

    # Connection to sbm schema
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_DRIVER: str = 'ODBC+Driver+17+for+SQL+Server'

settings = Settings(_env_file=".env", _env_file_encoding="utf-8") if os.path.exists(".env") else Settings()
