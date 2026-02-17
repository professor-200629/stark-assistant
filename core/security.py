"""
API security utilities for STARK v4.0
"""

import logging
import secrets
from typing import Optional
from .config import Config

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Security utilities for API authentication and authorization
    """
    
    @staticmethod
    def validate_api_key(api_key: Optional[str]) -> bool:
        """
        Validate API key against configured key
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid or authentication is disabled
        """
        # If authentication is disabled, always allow
        if not Config.ENABLE_API_KEY_AUTH:
            return True
        
        # If no API key is configured, allow (for development)
        if Config.API_KEY is None:
            logger.warning("API key authentication enabled but no key configured")
            return True
        
        # If no key provided by client, deny
        if api_key is None:
            logger.warning("API key authentication required but none provided")
            return False
        
        # Constant-time comparison to prevent timing attacks
        return secrets.compare_digest(api_key, Config.API_KEY)
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """
        Generate a secure random API key
        
        Args:
            length: Length of the key in bytes
            
        Returns:
            Hex-encoded API key
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def is_localhost_origin(origin: str) -> bool:
        """
        Check if origin is localhost
        
        Args:
            origin: Origin header value
            
        Returns:
            True if origin is localhost
        """
        localhost_patterns = [
            "http://localhost",
            "https://localhost",
            "http://127.0.0.1",
            "https://127.0.0.1",
        ]
        return any(origin.startswith(pattern) for pattern in localhost_patterns)
