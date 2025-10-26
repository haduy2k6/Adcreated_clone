import os
from dotenv import load_dotenv,set_key
from typing import Optional
from cryptography.fernet import Fernet
# Load .env file
load_dotenv()

class ConfigVar:
    """Centralized configuration management"""
    
    # ===== Redis Configuration =====
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_USERNAME: Optional[str] = os.getenv("REDIS_USERNAME")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # ===== Security Keys =====
    FERNET_KEY = os.getenv("FERNET_KEY")
    if not FERNET_KEY:
        FERNET_KEY = Fernet.generate_key()
        set_key(".env","FERNET_KEY", FERNET_KEY)

    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
    
    # ===== JWT Configuration =====
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "RS256")
    REFRESH_ALGORITHM: str = os.getenv("REFRESH_ALGORITHM", "HS256")
    
    # ===== Token Expiration =====
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10"))
    REFRESH_TOKEN_EXPIRE_SECONDS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_SECONDS", "604800"))  # 7 days
    
    # ===== OAuth Configuration =====
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    FACEBOOK_CLIENT_ID: Optional[str] = os.getenv("FACEBOOK_CLIENT_ID")
    FACEBOOK_CLIENT_SECRET: Optional[str] = os.getenv("FACEBOOK_CLIENT_SECRET")
    
    # ===== Application URLs =====
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # ===== Session Configuration =====
    SESSION_TTL: int = int(os.getenv("SESSION_TTL", "7200"))  # 2 hours
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    RATE_LIMIT_MAX: int = int(os.getenv("RATE_LIMIT_MAX", "100"))
    
    SENDER_MAIL = os.getenv("SENDER_MAIL")
    SENDER_PASS=os.getenv("SENDER_PASS")
    # ===== Validation =====
    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        errors = []
        
        if not cls.FERNET_KEY:
            errors.append("FERNET_KEY is required")
        
        if not cls.SECRET_KEY or cls.SECRET_KEY == "default-secret-key-change-in-production":
            errors.append("SECRET_KEY must be set to a secure value")
        
        if cls.REDIS_PASSWORD and not cls.REDIS_USERNAME:
            errors.append("REDIS_USERNAME required when REDIS_PASSWORD is set")
        
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
