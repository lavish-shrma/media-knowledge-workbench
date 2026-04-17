from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Document and Multimedia Q&A"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://USER:PASSWORD@HOST:5432/DB_NAME"
    uploads_dir: str = "./uploads"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    whisper_model: str = "base"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "SET_THIS_IN_ENVIRONMENT_USE_A_LONG_RANDOM_SECRET_KEY"
    jwt_algorithm: str = "HS256"
    access_token_exp_minutes: int = 60
    refresh_token_exp_days: int = 7
    rate_limit_per_minute: int = 30
    chat_cache_ttl_seconds: int = 300
    upload_cache_ttl_seconds: int = 3600

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
