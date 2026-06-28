from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    db_schema: str = "public"
    artifact_store: str = "s3"
    local_models_dir: str = "models_store"
    s3_bucket: str = ""
    s3_prefix: str = "models"
    aws_region: str = "us-east-1"
    aws_role_arn: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
