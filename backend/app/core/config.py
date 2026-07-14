from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = Field(default="Ariva API", alias="APP_NAME")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    app_env: str = Field(default="development", alias="APP_ENV")
    database_url: str = Field(default="sqlite:///./life_platform.db", alias="DATABASE_URL")
    cors_origins: str = Field(
        default=(
            "http://localhost:3000,http://127.0.0.1:3000,"
            "http://localhost:3001,http://127.0.0.1:3001,"
            "http://localhost:5174,http://127.0.0.1:5174,"
            "http://localhost:5173,http://127.0.0.1:5173,"
            "https://life-platform.vercel.app"
        ),
        alias="CORS_ORIGINS",
    )

    life_use_fixtures: bool = Field(default=False, alias="LIFE_USE_FIXTURES")
    life_cache_seconds: int = Field(default=180, alias="LIFE_CACHE_SECONDS")
    upstream_timeout_seconds: float = Field(default=8.0, alias="UPSTREAM_TIMEOUT_SECONDS")

    food_api_base: str = Field(default="https://food-platform-backend.fly.dev/api/v1", alias="FOOD_API_BASE")
    fuel_api_base: str = Field(default="https://octane-api.fly.dev", alias="FUEL_API_BASE")
    property_api_base: str = Field(
        default="https://property-price-intelligence-an-ardeno-production.fly.dev",
        alias="PROPERTY_API_BASE",
    )
    vehicle_api_base: str = Field(
        default="https://vehicle-platform-backend.fly.dev/api/v1",
        alias="VEHICLE_API_BASE",
    )

    firebase_project_id: str | None = Field(default=None, alias="FIREBASE_PROJECT_ID")
    firebase_credentials_json: str | None = Field(default=None, alias="FIREBASE_CREDENTIALS_JSON")
    firebase_credentials_path: str | None = Field(default=None, alias="FIREBASE_CREDENTIALS_PATH")
    life_test_auth_token: str | None = Field(default=None, alias="LIFE_TEST_AUTH_TOKEN")
    life_test_auth_sub: str = Field(default="test-user", alias="LIFE_TEST_AUTH_SUB")
    life_internal_token: str | None = Field(default=None, alias="LIFE_INTERNAL_TOKEN")

    @property
    def cors_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
