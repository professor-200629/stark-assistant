"""
Cancellation token management for hard stops in STARK v4.0
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CancellationToken:
    """
    Cancellation token for cooperative task cancellation
    """
    
    def __init__(self):
        """Initialize cancellation token"""
        self._cancelled: bool = False
        self._cancel_event: asyncio.Event = asyncio.Event()
        self._reason: Optional[str] = None
    
    @property
    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested"""
        return self._cancelled
    
    @property
    def cancel_reason(self) -> Optional[str]:
        """Get cancellation reason if available"""
        return self._reason
    
    def cancel(self, reason: Optional[str] = None):
        """
        Request cancellation
        
        Args:
            reason: Optional reason for cancellation
        """
        if not self._cancelled:
            self._cancelled = True
            self._reason = reason or "Cancellation requested"
            self._cancel_event.set()
            logger.info(f"Cancellation requested: {self._reason}")
    
    def raise_if_cancelled(self):
        """
        Raise exception if cancellation has been requested
        
        Raises:
            asyncio.CancelledError: If cancellation was requested
        """
        if self._cancelled:
            raise asyncio.CancelledError(self._reason)
    
    async def wait_for_cancellation(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for cancellation to be requested
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if cancelled, False if timeout
        """
        try:
            await asyncio.wait_for(self._cancel_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False
    
    def reset(self):
        """Reset the cancellation token"""
        self._cancelled = False
        self._cancel_event.clear()
        self._reason = None
        logger.debug("Cancellation token reset")
