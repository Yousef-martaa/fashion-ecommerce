from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Fashion E-Commerce API"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/fashion_ecommerce"

    # JWT auth. SECRET_KEY has a dev-only placeholder default -- it MUST be
    # overridden via .env (or another secrets mechanism) in any real deployment.
    SECRET_KEY: str = "insecure-dev-secret-change-me-before-deploying"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
