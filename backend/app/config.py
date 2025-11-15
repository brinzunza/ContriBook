from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings and configuration"""

    # Application
    APP_NAME: str = "ContriBook"
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str

    # Database
    DATABASE_URL: str
    BLOCKCHAIN_DB_PATH: str = "./blockchain.db"

    # Storage
    STORAGE_PATH: str = "./storage"
    ENCRYPTED_STORAGE_PATH: str = "./encrypted_storage"
    ARCHIVE_PATH: str = "./archives"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: str = ".pdf,.png,.jpg,.jpeg,.txt,.md,.doc,.docx"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_file_types_list(self) -> List[str]:
        return [ft.strip() for ft in self.ALLOWED_FILE_TYPES.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
