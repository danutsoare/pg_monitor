from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn


class Settings(BaseSettings):
    # Application settings
    PROJECT_NAME: str = "PostgreSQL Monitoring App"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:80"]
    
    # Scheduler settings
    SNAPSHOT_INTERVAL_MINUTES: int = 5 # Default interval in minutes
    
    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db" # Default to 'db' service name
    POSTGRES_PORT: str = "5432"
    
    # Optional: Directly use DATABASE_URL if provided
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            # If DATABASE_URL uses asyncpg, need to replace it for SQLAlchemy sync engine
            sync_url = str(self.DATABASE_URL).replace("postgresql+asyncpg://", "postgresql://")
            # Return the corrected URL as a string
            return sync_url
        else:
            # Fallback to individual components if DATABASE_URL is not set
            # Return the constructed URL as a string
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()