from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "WIYATA"
    app_base_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"

    platform_database_url: str = (
        "postgresql+asyncpg://wiyata:change-this-dev-password@127.0.0.1:5436/wiyata"
    )
    postgres_sandbox_url: str = (
        "postgresql://wiyata:change-this-dev-password@127.0.0.1:5436/wiyata"
    )
    mysql_sandbox_url: str = (
        "mysql://wiyata:change-this-dev-password@127.0.0.1:3307/wiyata_mysql"
    )
    redis_url: str = "redis://localhost:6379/0"
    app_secret_key: str = "change-this-secret"

    ai_provider: str = "none"
    ai_api_key: str = ""
    ollama_base_url: str = "http://ollama:11434"

    sandbox_default_ttl_minutes: int = 30
    sandbox_max_execution_seconds: int = 10
    sandbox_max_result_rows: int = 10000
    sandbox_max_result_bytes: int = 5_000_000
    sandbox_allow_ddl: bool = False
    sandbox_allow_dml: bool = False


settings = Settings()
