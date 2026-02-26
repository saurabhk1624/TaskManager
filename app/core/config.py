from functools import lru_cache
from pydantic import  Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = Field("task-manager", alias="APP_NAME")
    app_env: str = Field("development", alias="APP_ENV")
    log_level: str = Field("info", alias="LOG_LEVEL")

    mongo_uri: str = Field(..., alias="MONGO_URI")
    mongo_db_name: str = Field(..., alias="MONGO_DB_NAME")

    github_token: str = Field(..., alias="GITHUB_TOKEN")
    github_repo: str = Field(..., alias="GITHUB_REPO")

    port: int = Field(8000, alias="PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

