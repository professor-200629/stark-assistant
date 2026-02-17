"""
STARK v4.0 Core Package
Event-driven architecture with security and state management
"""

__version__ = "4.0.0"

from .events import Event, EventType
from .event_bus import EventBus
from .state_machine import StateMachine, State
from .cancellation import CancellationToken
from .config import Config

__all__ = [
    "Event",
    "EventType",
    "EventBus",
    "StateMachine",
    "State",
    "CancellationToken",
    "Config",
]
