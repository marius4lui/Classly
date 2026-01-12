from pydantic_settings import BaseSettings
from pydantic import EmailStr
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Classly"
    BASE_URL: str = "http://localhost:8000"

    # SMTP Settings
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str = "Classly <noreply@example.com>"
    SMTP_SECURE: bool = True

    # Email Settings
    EMAIL_NOTIFICATIONS_ENABLED: bool = True
    EMAIL_DIGEST_ENABLED: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
