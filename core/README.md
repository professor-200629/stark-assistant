# STARK v4.0 Core Module

## Overview

The core module provides the foundational architecture for STARK v4.0, implementing an event-driven system with security hardening and state management.

## Architecture Components

### 1. Events (`core/events.py`)

Event-driven architecture foundation with:

- **EventType**: Enum defining all system event types
  - State transitions
  - System events (start, stop, error)
  - User interactions (commands, queries)
  - Task management events
  - Health monitoring

- **Event**: Immutable dataclass for event objects
  - Auto-generated event IDs
  - Timezone-aware timestamps
  - Type-safe event data

### 2. Event Bus (`core/event_bus.py`)

Central pub/sub event system with:

- **Backpressure Management**: Queue size limits prevent memory leaks
- **Ring Buffer**: Fixed-size event history (no unbounded growth)
- **Exception Isolation**: Handler failures don't crash the system
- **Async Support**: Both sync and async event handlers
- **Non-blocking Publishing**: Events return immediately on queue full

### 3. State Machine (`core/state_machine.py`)

Finite state machine with guard rails:

- **Valid States**: idle, processing, responding, error, stopped
- **Transition Validation**: Only valid transitions allowed
- **Transition History**: Track state changes
- **Force Override**: Emergency state changes when needed

Valid transitions:
```
idle -> processing, stopped
processing -> responding, error, idle, stopped
responding -> idle, error, stopped
error -> idle, stopped
stopped -> idle
```

### 4. Cancellation Token (`core/cancellation.py`)

Cooperative cancellation for graceful shutdowns:

- **Non-forcing**: Tasks check cancellation status
- **Reason Tracking**: Record why cancellation occurred
- **Async Support**: Wait for cancellation events
- **Resettable**: Can be reused after reset

### 5. Configuration (`core/config.py`)

Environment-based configuration:

- **Environment Variables**: Override defaults via env vars
- **Security Defaults**: Localhost-only CORS, optional API keys
- **Production Ready**: Environment detection and appropriate defaults

Environment variables:
- `STARK_ENV`: Environment (development/production)
- `STARK_API_HOST`: API host (default: 127.0.0.1)
- `STARK_API_PORT`: API port (default: 8000)
- `STARK_API_KEY`: API key for authentication
- `STARK_ENABLE_API_KEY_AUTH`: Enable API key auth (default: false)
- `STARK_EVENT_QUEUE_MAX_SIZE`: Max event queue size (default: 1000)
- `STARK_EVENT_HISTORY_SIZE`: Event history ring buffer size (default: 100)
- `STARK_LOG_LEVEL`: Logging level (default: INFO)

### 6. Security (`core/security.py`)

Security utilities:

- **API Key Validation**: Constant-time comparison
- **API Key Generation**: Cryptographically secure random keys
- **Origin Validation**: Check for localhost origins

## Usage Examples

### Basic Event Flow

```python
from core import Event, EventType, EventBus

# Create event bus
bus = EventBus(max_queue_size=1000, history_size=100)

# Subscribe to events
async def handle_command(event: Event):
    print(f"Received command: {event.data}")

bus.subscribe(EventType.USER_COMMAND, handle_command)

# Publish events
event = Event(
    event_type=EventType.USER_COMMAND,
    data={"command": "hello"}
)
await bus.publish(event)

# Start processing (in background)
await bus.process_events()
```

### State Machine

```python
from core import StateMachine, State

# Create state machine
sm = StateMachine(initial_state=State.IDLE)

# Valid transition
sm.transition_to(State.PROCESSING)  # Returns True

# Invalid transition
sm.transition_to(State.RESPONDING)  # Returns False (not allowed from IDLE)

# Force transition
sm.transition_to(State.ERROR, force=True)  # Returns True
```

### Cancellation Token

```python
from core import CancellationToken
import asyncio

token = CancellationToken()

async def long_task(token):
    while not token.is_cancelled:
        # Do work
        await asyncio.sleep(1)
        token.raise_if_cancelled()  # Raises CancelledError if cancelled

# In another task
token.cancel("User requested stop")
```

## Testing

Run tests with:

```bash
# Core module tests
python3 -m unittest test_core -v

# API integration tests
python3 -m pytest test_api.py -v
```

## Security Features

1. **CORS Restrictions**: Only localhost origins allowed by default
2. **API Key Authentication**: Optional, recommended for production
3. **Backpressure**: Prevents memory exhaustion from event floods
4. **Exception Isolation**: Handler failures don't cascade
5. **Secure Defaults**: All security features enabled by default

## No External Dependencies

Core modules use only Python standard library:
- `asyncio` for async operations
- `dataclasses` for data structures
- `enum` for type-safe enums
- `logging` for diagnostics
- `collections.deque` for ring buffer
- `secrets` for cryptographic operations

## License

See LICENSE file in repository root.
