from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    allowed_hosts: str
    refresh_token_expire_days: int = 7
    access_token_expire_minutes: int = 15

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model_pro: str = "deepseek-v4-pro"
    deepseek_model_flash: str = "deepseek-v4-flash"
    redis_url: str = "redis://localhost:6379/0"

    # Search APIs
    serpapi_key: str = ""
    bing_api_key: str = ""

    # Development fallback: when True, run reports inline if Celery/Redis is unavailable
    run_reports_inline_when_celery_unavailable: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
