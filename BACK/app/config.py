from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str = Field(min_length=32)
    access_token_expire_minutes: int = 60
    frontend_origins: str = "http://localhost:5173"
    admin_email: str | None = None
    admin_password: str | None = None
    stripe_secret_key: str | None = None
    stripe_publishable_key: str | None = None
    stripe_webhook_secret: str | None = None
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def validate_stripe_keys(self) -> "Settings":
        secret_key = self.stripe_secret_key
        publishable_key = self.stripe_publishable_key
        if bool(secret_key) != bool(publishable_key):
            raise ValueError("Configure both Stripe test keys or leave both unset")
        if secret_key and publishable_key and (
            not secret_key.startswith("sk_test_")
            or not publishable_key.startswith("pk_test_")
        ):
            raise ValueError("Only Stripe test-mode keys (sk_test_ and pk_test_) are accepted")
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]

    @property
    def stripe_enabled(self) -> bool:
        return bool(
            self.stripe_secret_key
            and self.stripe_secret_key.startswith("sk_test_")
            and self.stripe_publishable_key
            and self.stripe_publishable_key.startswith("pk_test_")
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
