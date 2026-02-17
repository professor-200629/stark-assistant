"""
Event type definitions and Event dataclass for STARK v4.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict
from datetime import datetime, timezone
import uuid


class EventType(Enum):
    """Event types for STARK system"""
    
    # State transitions
    STATE_CHANGE = "state_change"
    
    # System events
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    SYSTEM_ERROR = "system_error"
    
    # User interactions
    USER_COMMAND = "user_command"
    USER_QUERY = "user_query"
    
    # Task events
    TASK_CREATE = "task_create"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    TASK_CANCEL = "task_cancel"
    
    # Response events
    RESPONSE_READY = "response_ready"
    
    # Health monitoring
    HEALTH_CHECK = "health_check"
    HEALTH_STATUS = "health_status"


@dataclass
class Event:
    """
    Immutable event object for event-driven architecture
    """
    
    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:16]}")
    
    def __post_init__(self):
        """Ensure event_type is an EventType enum"""
        if isinstance(self.event_type, str):
            self.event_type = EventType(self.event_type)
