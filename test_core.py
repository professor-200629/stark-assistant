"""
Tests for STARK v4.0 core modules
"""

import asyncio
import unittest
from datetime import datetime

from core import (
    Event,
    EventType,
    EventBus,
    StateMachine,
    State,
    CancellationToken,
    Config,
)
from core.security import SecurityManager


class TestEvents(unittest.TestCase):
    """Test event types and Event dataclass"""
    
    def test_event_creation(self):
        """Test creating an event"""
        event = Event(
            event_type=EventType.USER_COMMAND,
            data={"command": "test"},
        )
        self.assertEqual(event.event_type, EventType.USER_COMMAND)
        self.assertEqual(event.data["command"], "test")
        self.assertIsInstance(event.timestamp, datetime)
        self.assertTrue(event.event_id.startswith("evt_"))
    
    def test_event_type_from_string(self):
        """Test creating event from string event type"""
        event = Event(event_type="user_command", data={})
        self.assertEqual(event.event_type, EventType.USER_COMMAND)


class TestStateMachine(unittest.TestCase):
    """Test state machine functionality"""
    
    def test_initial_state(self):
        """Test state machine initialization"""
        sm = StateMachine(initial_state=State.IDLE)
        self.assertEqual(sm.current_state, State.IDLE)
        self.assertIsNone(sm.previous_state)
    
    def test_valid_transition(self):
        """Test valid state transition"""
        sm = StateMachine(initial_state=State.IDLE)
        result = sm.transition_to(State.PROCESSING)
        self.assertTrue(result)
        self.assertEqual(sm.current_state, State.PROCESSING)
        self.assertEqual(sm.previous_state, State.IDLE)
    
    def test_invalid_transition(self):
        """Test invalid state transition is blocked"""
        sm = StateMachine(initial_state=State.IDLE)
        result = sm.transition_to(State.RESPONDING)
        self.assertFalse(result)
        self.assertEqual(sm.current_state, State.IDLE)
    
    def test_force_transition(self):
        """Test forcing an invalid transition"""
        sm = StateMachine(initial_state=State.IDLE)
        result = sm.transition_to(State.RESPONDING, force=True)
        self.assertTrue(result)
        self.assertEqual(sm.current_state, State.RESPONDING)
    
    def test_transition_history(self):
        """Test transition history tracking"""
        sm = StateMachine(initial_state=State.IDLE)
        sm.transition_to(State.PROCESSING)
        sm.transition_to(State.RESPONDING)
        
        history = sm.get_transition_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0], (State.IDLE, State.PROCESSING))
        self.assertEqual(history[1], (State.PROCESSING, State.RESPONDING))


class TestCancellationToken(unittest.TestCase):
    """Test cancellation token functionality"""
    
    def test_initial_state(self):
        """Test token initial state"""
        token = CancellationToken()
        self.assertFalse(token.is_cancelled)
        self.assertIsNone(token.cancel_reason)
    
    def test_cancel(self):
        """Test cancelling token"""
        token = CancellationToken()
        token.cancel("Test cancellation")
        self.assertTrue(token.is_cancelled)
        self.assertEqual(token.cancel_reason, "Test cancellation")
    
    def test_raise_if_cancelled(self):
        """Test raising exception on cancellation"""
        token = CancellationToken()
        token.cancel("Test")
        with self.assertRaises(asyncio.CancelledError):
            token.raise_if_cancelled()
    
    def test_reset(self):
        """Test resetting token"""
        token = CancellationToken()
        token.cancel("Test")
        token.reset()
        self.assertFalse(token.is_cancelled)
        self.assertIsNone(token.cancel_reason)


class TestEventBus(unittest.IsolatedAsyncioTestCase):
    """Test event bus functionality"""
    
    async def test_publish_event(self):
        """Test publishing an event"""
        bus = EventBus(max_queue_size=10, history_size=5)
        event = Event(event_type=EventType.USER_COMMAND, data={})
        result = await bus.publish(event)
        self.assertTrue(result)
        self.assertEqual(bus.get_queue_size(), 1)
    
    async def test_event_history(self):
        """Test event history ring buffer"""
        bus = EventBus(max_queue_size=10, history_size=3)
        
        # Publish 5 events
        for i in range(5):
            await bus.publish(Event(event_type=EventType.USER_COMMAND, data={"i": i}))
        
        # History should only contain last 3
        history = bus.get_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[-1].data["i"], 4)
    
    async def test_backpressure(self):
        """Test backpressure when queue is full"""
        bus = EventBus(max_queue_size=2, history_size=5)
        
        # Fill queue
        await bus.publish(Event(event_type=EventType.USER_COMMAND, data={"n": 1}))
        await bus.publish(Event(event_type=EventType.USER_COMMAND, data={"n": 2}))
        
        # Next publish should fail due to backpressure
        result = await bus.publish(Event(event_type=EventType.USER_COMMAND, data={"n": 3}))
        self.assertFalse(result)
        self.assertTrue(bus.is_queue_full())
    
    async def test_subscribe_and_dispatch(self):
        """Test subscribing to events and dispatching"""
        bus = EventBus()
        received_events = []
        
        def handler(event):
            received_events.append(event)
        
        bus.subscribe(EventType.USER_COMMAND, handler)
        
        event = Event(event_type=EventType.USER_COMMAND, data={"test": True})
        await bus.publish(event)
        
        # Process one event
        await bus._dispatch_event(event)
        
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0].event_type, EventType.USER_COMMAND)


class TestConfig(unittest.TestCase):
    """Test configuration"""
    
    def test_default_values(self):
        """Test default configuration values"""
        self.assertEqual(Config.APP_NAME, "STARK v4.0")
        self.assertEqual(Config.APP_VERSION, "4.0.0")
        self.assertIsInstance(Config.CORS_ALLOWED_ORIGINS, list)
    
    def test_environment_detection(self):
        """Test environment detection methods"""
        # Default should be development
        self.assertTrue(Config.is_development() or Config.is_production())


class TestSecurity(unittest.TestCase):
    """Test security utilities"""
    
    def test_generate_api_key(self):
        """Test API key generation"""
        key = SecurityManager.generate_api_key()
        self.assertIsInstance(key, str)
        self.assertEqual(len(key), 64)  # 32 bytes = 64 hex chars
    
    def test_localhost_origin_check(self):
        """Test localhost origin validation"""
        self.assertTrue(SecurityManager.is_localhost_origin("http://localhost:3000"))
        self.assertTrue(SecurityManager.is_localhost_origin("http://127.0.0.1:8000"))
        self.assertFalse(SecurityManager.is_localhost_origin("http://example.com"))


if __name__ == "__main__":
    unittest.main()
