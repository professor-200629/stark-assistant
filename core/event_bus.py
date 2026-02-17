"""
Central pub/sub event system with backpressure management for STARK v4.0
"""

import asyncio
import logging
from collections import deque
from typing import Callable, Dict, List, Optional
from .events import Event, EventType

logger = logging.getLogger(__name__)


class EventBus:
    """
    Central event bus with pub/sub pattern and backpressure management
    """
    
    def __init__(self, max_queue_size: int = 1000, history_size: int = 100):
        """
        Initialize event bus
        
        Args:
            max_queue_size: Maximum size of event queue (backpressure limit)
            history_size: Size of ring buffer for event history
        """
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._event_history: deque = deque(maxlen=history_size)
        self._processing: bool = False
        self._max_queue_size: int = max_queue_size
        
    def subscribe(self, event_type: EventType, handler: Callable):
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async or sync callback function
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed handler to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """
        Unsubscribe from an event type
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Callback function to remove
        """
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            logger.debug(f"Unsubscribed handler from {event_type.value}")
    
    async def publish(self, event: Event) -> bool:
        """
        Publish an event to the bus
        
        Args:
            event: Event to publish
            
        Returns:
            True if event was queued, False if queue is full (backpressure)
        """
        try:
            # Non-blocking put with immediate return on full queue
            self._event_queue.put_nowait(event)
            self._event_history.append(event)
            logger.debug(f"Published event: {event.event_type.value}")
            return True
        except asyncio.QueueFull:
            logger.warning(f"Event queue full, dropping event: {event.event_type.value}")
            return False
    
    async def process_events(self):
        """
        Process events from the queue (should run in background task)
        """
        self._processing = True
        logger.info("Event bus processing started")
        
        while self._processing:
            try:
                # Wait for next event with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                await self._dispatch_event(event)
            except asyncio.TimeoutError:
                # No events, continue loop
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}", exc_info=True)
    
    async def _dispatch_event(self, event: Event):
        """
        Dispatch event to all subscribers
        
        Args:
            event: Event to dispatch
        """
        handlers = self._subscribers.get(event.event_type, [])
        
        for handler in handlers:
            try:
                # Handle both sync and async handlers
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                # Isolate handler exceptions to prevent cascade failures
                logger.error(
                    f"Error in event handler for {event.event_type.value}: {e}",
                    exc_info=True
                )
    
    def stop_processing(self):
        """Stop the event processing loop"""
        self._processing = False
        logger.info("Event bus processing stopped")
    
    def get_history(self, limit: Optional[int] = None) -> List[Event]:
        """
        Get event history
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        history = list(self._event_history)
        if limit:
            history = history[-limit:]
        return history
    
    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self._event_queue.qsize()
    
    def is_queue_full(self) -> bool:
        """Check if queue is at capacity"""
        return self._event_queue.qsize() >= self._max_queue_size
