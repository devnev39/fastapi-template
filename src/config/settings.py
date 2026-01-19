import secrets
import string

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.environments import Environments

chars = string.digits + string.ascii_letters + string.punctuation


def create_random(length: int = 32) -> str:
    """Create random string."""
    return "".join([secrets.choice(chars) for _ in range(length)])


class EnvSettings(BaseSettings):
    """Base environment settings for a specific environment."""

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")
    PROJECT_NAME: str = "FastAPI Auth"
    MONGO_URI: str = "mongodb://localhost:27017"
    ENV: str = Environments().TEST
    DB_NAME: str = Environments().TEST_DB_NAME
    TOKEN_EXPIRY_PERIOD: int = 30  # In minutes
    JWT_SECRET: str = create_random()
    APP_LOGGER_LEVEL: int = 10
    APP_LOGGER_ADDRESS: str | None = None
    APP_LOGGER_PORT: int | None = None

    JWT_ALGORITHM: str = "HS256"
    APP_LOGGER_SYS_LOG: bool = False
    ORIGINS: str = Environments().ORIGINS
    ROOT_USERNAME: SecretStr = SecretStr(create_random())
    ROOT_PASSWORD: SecretStr = SecretStr(create_random())
    MAIL_HOST: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str | None = None
    MAIL_PASSWORD: str | None = None
    ENABLE_MAIL: bool = True

    def get_origins(self) -> list[str]:
        """Get list of origings."""
        return self.ORIGINS.split(",")


class Settings(EnvSettings, Environments):
    def __init__(self):
        super().__init__()
        if self.ENV == self.TEST and not self.APP_LOGGER_SYS_LOG:
            self.APP_LOGGER_ADDRESS = None
            self.APP_LOGGER_PORT = None


settings = Settings()
