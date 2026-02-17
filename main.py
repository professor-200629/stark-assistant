"""
STARK v4.0 Main Application
FastAPI-based event-driven architecture with security hardening
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from core import (
    Config,
    Event,
    EventType,
    EventBus,
    StateMachine,
    State,
    CancellationToken,
)
from core.security import SecurityManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global instances
event_bus: Optional[EventBus] = None
state_machine: Optional[StateMachine] = None
cancellation_token: Optional[CancellationToken] = None
background_tasks: List[asyncio.Task] = []


def ensure_initialized():
    """Ensure global instances are initialized (for testing)"""
    global event_bus, state_machine, cancellation_token
    
    if event_bus is None:
        event_bus = EventBus(
            max_queue_size=Config.EVENT_QUEUE_MAX_SIZE,
            history_size=Config.EVENT_HISTORY_SIZE,
        )
    
    if state_machine is None:
        state_machine = StateMachine(initial_state=State.IDLE)
    
    if cancellation_token is None:
        cancellation_token = CancellationToken()
    
    return event_bus, state_machine, cancellation_token


# Pydantic models for API
class EventRequest(BaseModel):
    """Request model for posting events"""
    event_type: str
    data: Dict = {}


class StateResponse(BaseModel):
    """Response model for state information"""
    current_state: str
    previous_state: Optional[str]


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    state: str
    queue_size: int
    queue_full: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown
    """
    global event_bus, state_machine, cancellation_token, background_tasks
    
    # Startup
    logger.info(f"Starting {Config.APP_NAME} {Config.APP_VERSION}")
    
    # Initialize core components
    event_bus = EventBus(
        max_queue_size=Config.EVENT_QUEUE_MAX_SIZE,
        history_size=Config.EVENT_HISTORY_SIZE,
    )
    state_machine = StateMachine(initial_state=State.IDLE)
    cancellation_token = CancellationToken()
    
    # Start event processing in background
    event_processing_task = asyncio.create_task(event_bus.process_events())
    background_tasks.append(event_processing_task)
    
    # Publish system start event
    await event_bus.publish(
        Event(event_type=EventType.SYSTEM_START, data={"version": Config.APP_VERSION})
    )
    
    logger.info("STARK v4.0 started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down STARK v4.0")
    
    # Publish system stop event
    await event_bus.publish(Event(event_type=EventType.SYSTEM_STOP))
    
    # Stop event processing
    event_bus.stop_processing()
    cancellation_token.cancel("System shutdown")
    
    # Cancel background tasks
    for task in background_tasks:
        task.cancel()
    
    # Wait for tasks to complete
    await asyncio.gather(*background_tasks, return_exceptions=True)
    
    logger.info("STARK v4.0 shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=Config.APP_NAME,
    version=Config.APP_VERSION,
    description="Event-driven AI assistant with security hardening",
    lifespan=lifespan,
)

# Configure CORS - restricted to localhost only
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# API Key validation dependency
async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """Validate API key if authentication is enabled"""
    if not SecurityManager.validate_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": Config.APP_NAME,
        "version": Config.APP_VERSION,
        "status": "running",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    ensure_initialized()
    return HealthResponse(
        status="healthy",
        version=Config.APP_VERSION,
        state=state_machine.current_state.value,
        queue_size=event_bus.get_queue_size(),
        queue_full=event_bus.is_queue_full(),
    )


@app.get("/state", response_model=StateResponse)
async def get_state(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """Get current state (requires API key if enabled)"""
    await verify_api_key(x_api_key)
    ensure_initialized()
    
    return StateResponse(
        current_state=state_machine.current_state.value,
        previous_state=state_machine.previous_state.value if state_machine.previous_state else None,
    )


@app.post("/events")
async def post_event(
    event_req: EventRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Post an event to the system (requires API key if enabled)
    """
    await verify_api_key(x_api_key)
    ensure_initialized()
    
    try:
        # Validate event type
        event_type = EventType(event_req.event_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event type: {event_req.event_type}",
        )
    
    # Create and publish event
    event = Event(event_type=event_type, data=event_req.data)
    
    if not await event_bus.publish(event):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Event queue full - backpressure active",
        )
    
    return {
        "status": "queued",
        "event_id": event.event_id,
        "event_type": event.event_type.value,
    }


@app.get("/events/history")
async def get_event_history(
    limit: int = 10,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Get event history from ring buffer (requires API key if enabled)
    """
    await verify_api_key(x_api_key)
    ensure_initialized()
    
    history = event_bus.get_history(limit=limit)
    
    return {
        "count": len(history),
        "events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type.value,
                "timestamp": e.timestamp.isoformat(),
                "data": e.data,
            }
            for e in history
        ],
    }


@app.get("/state/transitions")
async def get_state_transitions(
    limit: int = 10,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Get state transition history (requires API key if enabled)
    """
    await verify_api_key(x_api_key)
    ensure_initialized()
    
    transitions = state_machine.get_transition_history(limit=limit)
    
    return {
        "count": len(transitions),
        "transitions": [
            {
                "from": from_state.value if from_state else None,
                "to": to_state.value,
            }
            for from_state, to_state in transitions
        ],
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Publish error event
    if event_bus:
        await event_bus.publish(
            Event(
                event_type=EventType.SYSTEM_ERROR,
                data={"error": str(exc), "path": str(request.url)},
            )
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        log_level=Config.LOG_LEVEL.lower(),
        reload=Config.is_development(),
    )