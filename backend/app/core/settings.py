from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CORS_ALLOW_HOSTS: list[str] = []

    GEMINI_API_KEY: str | None = None
    GEMINI_API_BASE: str | None = None
    GEMINI_MODEL: str = "gemini-3.1-flash-lite-preview"

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()  # type: ignore
