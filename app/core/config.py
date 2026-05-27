from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Billing Platform"
    environment: str = "local"
    debug: bool = True

    database_url: str = "sqlite:///./billing_platform.db"

    fake_provider_webhook_secret: str = "local-dev-secret"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()