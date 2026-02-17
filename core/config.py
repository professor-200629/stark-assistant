"""
Environment-based configuration with security defaults for STARK v4.0
"""

import os
from typing import Optional


class Config:
    """
    Configuration manager with environment variable support and secure defaults
    """
    
    # Application settings
    APP_NAME: str = "STARK v4.0"
    APP_VERSION: str = "4.0.0"
    ENVIRONMENT: str = os.getenv("STARK_ENV", "development")
    
    # API settings
    API_HOST: str = os.getenv("STARK_API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("STARK_API_PORT", "8000"))
    
    # Security settings - API key is optional but recommended for production
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY: Optional[str] = os.getenv("STARK_API_KEY")
    ENABLE_API_KEY_AUTH: bool = os.getenv("STARK_ENABLE_API_KEY_AUTH", "false").lower() == "true"
    
    # CORS settings - restricted to localhost only by default
    CORS_ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Event system settings
    EVENT_QUEUE_MAX_SIZE: int = int(os.getenv("STARK_EVENT_QUEUE_MAX_SIZE", "1000"))
    EVENT_HISTORY_SIZE: int = int(os.getenv("STARK_EVENT_HISTORY_SIZE", "100"))
    EVENT_PROCESSING_TIMEOUT: float = float(os.getenv("STARK_EVENT_TIMEOUT", "5.0"))
    
    # State machine settings
    DEFAULT_STATE: str = "idle"
    ALLOWED_STATES: list = ["idle", "processing", "responding", "error", "stopped"]
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("STARK_LOG_LEVEL", "INFO")
    ENABLE_DEBUG_LOGGING: bool = ENVIRONMENT == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development environment"""
        return cls.ENVIRONMENT == "development"
    
    @classmethod
    def validate_api_key(cls, api_key: str) -> bool:
        """
        Validate API key if authentication is enabled
        
        Note: Use SecurityManager.validate_api_key for actual validation
        This method is kept for backwards compatibility
        """
        from .security import SecurityManager
        return SecurityManager.validate_api_key(api_key)
