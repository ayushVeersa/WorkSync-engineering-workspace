from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum

class Environment(str, Enum):
    dev = "dev"
    test = "test"
    prod = "prod"

class Settings(BaseSettings):
    app_name: str = "Engineer workspace"
    debug: bool = False
    db_url: str
    jwt_secret: str
    jwt_expiry: int
    algorithm: str
    environment: Environment = Environment.dev

    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_from: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

