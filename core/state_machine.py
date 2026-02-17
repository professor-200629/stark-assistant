"""
State machine with guard rails and valid transition enforcement for STARK v4.0
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class State(Enum):
    """Valid states for STARK system"""
    
    IDLE = "idle"
    PROCESSING = "processing"
    RESPONDING = "responding"
    ERROR = "error"
    STOPPED = "stopped"


class StateMachine:
    """
    State machine with guard rails and transition validation
    """
    
    # Valid state transitions
    VALID_TRANSITIONS: Dict[State, Set[State]] = {
        State.IDLE: {State.PROCESSING, State.STOPPED},
        State.PROCESSING: {State.RESPONDING, State.ERROR, State.IDLE, State.STOPPED},
        State.RESPONDING: {State.IDLE, State.ERROR, State.STOPPED},
        State.ERROR: {State.IDLE, State.STOPPED},
        State.STOPPED: {State.IDLE},
    }
    
    def __init__(self, initial_state: State = State.IDLE):
        """
        Initialize state machine
        
        Args:
            initial_state: Starting state
        """
        self._current_state: State = initial_state
        self._previous_state: Optional[State] = None
        self._transition_history: List[tuple] = []
        logger.info(f"State machine initialized in {initial_state.value} state")
    
    @property
    def current_state(self) -> State:
        """Get current state"""
        return self._current_state
    
    @property
    def previous_state(self) -> Optional[State]:
        """Get previous state"""
        return self._previous_state
    
    def can_transition_to(self, target_state: State) -> bool:
        """
        Check if transition to target state is valid
        
        Args:
            target_state: State to transition to
            
        Returns:
            True if transition is valid
        """
        return target_state in self.VALID_TRANSITIONS.get(self._current_state, set())
    
    def transition_to(self, target_state: State, force: bool = False) -> bool:
        """
        Transition to a new state with validation
        
        Args:
            target_state: State to transition to
            force: Force transition even if invalid (use with caution)
            
        Returns:
            True if transition succeeded
        """
        if not force and not self.can_transition_to(target_state):
            logger.warning(
                f"Invalid state transition: {self._current_state.value} -> {target_state.value}"
            )
            return False
        
        self._previous_state = self._current_state
        self._current_state = target_state
        
        # Record transition
        self._transition_history.append((self._previous_state, target_state))
        
        logger.info(
            f"State transition: {self._previous_state.value} -> {target_state.value}"
        )
        return True
    
    def reset(self):
        """Reset to initial idle state"""
        self.transition_to(State.IDLE, force=True)
        logger.info("State machine reset to IDLE")
    
    def get_transition_history(self, limit: Optional[int] = None) -> List[tuple]:
        """
        Get state transition history
        
        Args:
            limit: Maximum number of transitions to return
            
        Returns:
            List of (from_state, to_state) tuples
        """
        history = self._transition_history
        if limit:
            history = history[-limit:]
        return history
    
    def is_in_state(self, state: State) -> bool:
        """
        Check if currently in a specific state
        
        Args:
            state: State to check
            
        Returns:
            True if in specified state
        """
        return self._current_state == state
