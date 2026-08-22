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
    # Comma-separated list of allowed frontend origins for CORS. Defaults to
    # local dev; set to the deployed frontend's real origin(s) in production
    # (e.g. https://your-app.vercel.app) — see app/main.py's CORSMiddleware.
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
