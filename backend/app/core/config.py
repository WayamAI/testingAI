from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "wayam_testing_cloud"
    jwt_secret: str = "change-me-in-local-env"
    jwt_expire_minutes: int = 1440
    demo_mode: bool = True
    redis_url: str = "redis://localhost:6379"
    ollama_base_url: str = "https://ollama.com"
    ollama_api_key: str = ""
    ollama_model: str = "gpt-oss:120b-cloud"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
