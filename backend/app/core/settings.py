from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CORS_ALLOW_HOSTS: list[str] = []

    # LiteLLM configuration
    LITELLM_MODEL: str | None = None  # e.g., "gemini/gemini-3.1-flash-lite-preview", "openai/gpt-4o"
    LITELLM_API_BASE: str | None = None  # Custom proxy URL (optional)
    LITELLM_API_KEY: str | None = None  # API key for the provider

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()  # type: ignore
