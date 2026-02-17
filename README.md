# STARK v4.0: Event-Driven AI Assistant

## Overview

STARK v4.0 is a sophisticated personal AI assistant built on a modern event-driven architecture with security hardening and production-ready foundations. This release focuses on establishing a robust, scalable, and secure platform for AI-powered task management and user interactions.

## What's New in v4.0

### Event-Driven Architecture
- **Central Event Bus**: Pub/sub pattern with backpressure management
- **Ring Buffer**: Fixed-size event history prevents memory leaks
- **Exception Isolation**: Handler failures don't cascade through the system
- **Async-First**: Native async/await support throughout

### Security Hardening
- **Restricted CORS**: Localhost-only by default
- **API Key Authentication**: Optional, production-ready authentication
- **Secure Defaults**: All security features enabled out of the box
- **Constant-Time Comparison**: Prevents timing attacks on API keys

### State Machine Foundation
- **Guard Rails**: Only valid state transitions allowed
- **Transition History**: Full audit trail of state changes
- **Force Override**: Emergency controls when needed

### Production Ready
- **Environment-Based Config**: Environment variables for all settings
- **Comprehensive Logging**: Structured logging with configurable levels
- **Health Monitoring**: Built-in health check endpoints
- **Graceful Shutdown**: Proper cleanup and resource management

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/professor-200629/stark-assistant.git
cd stark-assistant

# Install dependencies
pip install -r requirements.txt
```

### Running STARK v4.0

```bash
# Run with default settings (development mode)
python3 main.py

# Run with custom settings
export STARK_API_PORT=9000
export STARK_LOG_LEVEL=DEBUG
python3 main.py
```

### API Endpoints

Once running, the API is available at `http://127.0.0.1:8000`:

- `GET /` - Root endpoint with app info
- `GET /health` - Health check with system status
- `GET /state` - Current state machine state
- `POST /events` - Post events to the system
- `GET /events/history` - Retrieve event history
- `GET /state/transitions` - State transition history

### Example API Usage

```bash
# Check health
curl http://127.0.0.1:8000/health

# Post an event
curl -X POST http://127.0.0.1:8000/events \
  -H "Content-Type: application/json" \
  -d '{"event_type": "user_command", "data": {"command": "hello"}}'

# Get event history
curl http://127.0.0.1:8000/events/history?limit=10
```

## Architecture

### Core Modules

- **core/config.py** - Environment-based configuration
- **core/events.py** - Event types and Event dataclass
- **core/event_bus.py** - Central pub/sub event system
- **core/state_machine.py** - State machine with guard rails
- **core/cancellation.py** - Cancellation token management
- **core/security.py** - API security utilities

See [core/README.md](core/README.md) for detailed documentation.

## Features

### Current (v4.0)
- ✅ Event-driven architecture
- ✅ FastAPI-based REST API
- ✅ State machine with validation
- ✅ Security hardening (CORS, API keys)
- ✅ Backpressure management
- ✅ Health monitoring
- ✅ Comprehensive logging

### Planned (Future Releases)
- 🔄 Voice capabilities and audio engine (v4.1)
- 🔄 Task management with persistence
- 🔄 Natural language processing
- 🔄 Calendar integration
- 🔄 Communication modules
- 🔄 Smart home integration

## Configuration

Configure STARK via environment variables:

```bash
# Environment
export STARK_ENV=production

# API Settings
export STARK_API_HOST=0.0.0.0
export STARK_API_PORT=8000

# Security
export STARK_API_KEY=your-secret-key-here
export STARK_ENABLE_API_KEY_AUTH=true

# Event System
export STARK_EVENT_QUEUE_MAX_SIZE=1000
export STARK_EVENT_HISTORY_SIZE=100

# Logging
export STARK_LOG_LEVEL=INFO
```

## Testing

```bash
# Run core module tests
python3 -m unittest test_core -v

# Run API integration tests
python3 -m pytest test_api.py -v
```

## Security

- **CORS**: Restricted to localhost origins by default
- **API Keys**: Optional authentication with constant-time comparison
- **Backpressure**: Queue limits prevent memory exhaustion
- **Exception Isolation**: Handler failures are contained
- **Secure Defaults**: All security features enabled by default

## Dependencies

STARK v4.0 uses minimal, well-maintained dependencies:

- **FastAPI** - Modern, fast web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation (included with FastAPI)

Core modules use only Python standard library.

## License

See LICENSE file for details.

## Contributing

STARK is actively developed. Contributions welcome!

## Version History

- **v4.0.0** (Current) - Event-driven architecture foundation
- **v1.0.0** - Initial release