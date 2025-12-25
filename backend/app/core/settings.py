from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CORS_ALLOW_HOSTS: list[str] = []

    GEMINI_API_KEY: str | None = None

    # LiteLLM configuration for multi-provider support
    LITELLM_MODEL: str | None = None  # e.g., "openai/gpt-4o", "anthropic/claude-3-5-sonnet"
    LITELLM_API_BASE: str | None = None  # Custom proxy URL (optional)
    LITELLM_API_KEY: str | None = None  # API key for the proxy/provider

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()  # type: ignore
