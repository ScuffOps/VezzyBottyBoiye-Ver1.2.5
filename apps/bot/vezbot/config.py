"""Bot configuration from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Discord
    discord_token: str
    discord_client_id: str
    discord_client_secret: str
    discord_redirect_uri: str

    # Database
    database_url: str

    # Redis (optional)
    redis_url: str | None = None

    # Twitch
    twitch_client_id: str | None = None
    twitch_client_secret: str | None = None

    # Application
    base_url: str = "http://localhost:8000"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
