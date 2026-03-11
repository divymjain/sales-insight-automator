from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production-use-secrets-manager"
    API_KEY_HEADER: str = "X-API-Key"
    INTERNAL_API_KEY: str = "dev-api-key-change-in-production"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.vercel.app",
    ]

    # LLM
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"  # "gemini" or "groq"

    # Email
    EMAIL_PROVIDER: str = "smtp"  # "sendgrid" or "smtp"
    SENDGRID_API_KEY: str = ""
    RESEND_API_KEY: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@rabbittai.com"
    FROM_NAME: str = "Rabbitt AI Sales Insights"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    MAX_FILE_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
