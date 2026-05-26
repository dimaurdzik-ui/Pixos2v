from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path
import os

_ENV_FILE = Path(__file__).parent.parent.parent / ".env"  # apps/api/.env

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pixos v2 Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # Environment
    ENVIRONMENT: str = "development" # development, production
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL

    # Supabase (Auth) - Deprecated for Clerk
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # Encryption (Fernet key)
    SYSTEM_SECRET_KEY: str = os.environ.get("SYSTEM_SECRET_KEY", "b3k12j3h12bk3j12b3kj12b3kj12b3k1j2b3k12j3hk=")

    # Stripe Billing
    STRIPE_SECRET_KEY: str | None = os.environ.get("STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str | None = os.environ.get("STRIPE_WEBHOOK_SECRET")

    # Clerk (Auth)
    CLERK_SECRET_KEY: Optional[str] = None
    CLERK_ISSUER_URL: Optional[str] = None

    # Redis/Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LangGraph & Tools
    MOCK_TOOLS: bool = True
    
    # LLM (LiteLLM)
    OPENAI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), case_sensitive=True, extra="ignore")
    
    def model_post_init(self, __context: type) -> None:
        if self.ENVIRONMENT == "production" and self.MOCK_TOOLS is True:
            raise ValueError("Cannot run with MOCK_TOOLS=True in production environment")

settings = Settings()
