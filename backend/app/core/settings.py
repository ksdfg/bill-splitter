from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CORS_ALLOW_HOSTS: list[str] = []

    GEMINI_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()  # type: ignore
print(settings.GEMINI_API_KEY, settings.CORS_ALLOW_HOSTS)
