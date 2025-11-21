from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Centralized application settings.
    Pydantic-settings reads configuration from environment variables.
    """
    # Database configuration
    SQLALCHEMY_DATABASE_URL: str

    # MinIO configuration
    MINIO_ENDPOINT: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str

    # Redis configuration for Celery
    REDIS_URL: str

    # JWT Authentication
    SECRET_KEY: str = "a_very_secret_key_that_should_be_changed"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # model_config allows pydantic to load variables from a .env file for local development
    # In production (Docker), these will be passed directly as environment variables.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Create a single, importable instance of the settings
settings = Settings()