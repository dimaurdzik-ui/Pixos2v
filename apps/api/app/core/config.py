from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Pixos v2 Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.DATABASE_URL

    # Supabase (Auth)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None

    # Redis/Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LangGraph & Tools
    MOCK_TOOLS: bool = True
    
    # LLM (LiteLLM)
    OPENAI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
