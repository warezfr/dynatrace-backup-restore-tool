import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Dynatrace Backup Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/dynatrace_backup.db"
    
    # Dynatrace Managed
    DYNATRACE_ENVIRONMENT_URL: str = ""  # Ex: https://dynatrace.example.com/e/12345678
    DYNATRACE_API_TOKEN: str = ""
    DYNATRACE_INSECURE_SSL: bool = False  # Pour certificats custom
    
    # Monaco CLI
    MONACO_CLI_PATH: str = str(BASE_DIR / "bin" / "monaco")
    MONACO_TIMEOUT: int = 300  # secondes
    
    # Backups
    BACKUP_DIR: str = str(BASE_DIR / "backups")
    BACKUP_RETENTION_DAYS: int = 30
    
    # Scheduling
    SCHEDULER_ENABLED: bool = True
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
