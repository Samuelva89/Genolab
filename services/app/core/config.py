import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # SECURITY WARNING: Generate a strong SECRET_KEY and set it in .env file
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "INSECURE-DEV-KEY-CHANGE-IN-PRODUCTION")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./funjilapv1.db"

    # Redis / Celery
    REDIS_PASSWORD: Optional[str] = None
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Application
    APP_NAME: str = "FunjiLapV1 API"
    APP_VERSION: str = "0.3.0"
    DEBUG: bool = True

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = "fasta,fastq,gb,gff,fa,fq"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()

# Validation: Warn if using default SECRET_KEY
if settings.SECRET_KEY == "INSECURE-DEV-KEY-CHANGE-IN-PRODUCTION":
    import warnings
    warnings.warn(
        "WARNING: Using default SECRET_KEY! Set SECRET_KEY in .env file for production.",
        UserWarning
    )
