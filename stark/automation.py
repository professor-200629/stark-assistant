"""
stark/automation.py – System-automation helpers for STARK.

Delegates to system_control.SystemControl, adding a security guard so that
destructive operations (shutdown, restart) require PIN confirmation when
``STARK_SECURITY_PIN`` is set in the environment.
"""

import os

from system_control import SystemControl  # type: ignore

# Actions that must never execute without user authentication
DESTRUCTIVE_ACTIONS: frozenset = frozenset({"shutdown", "restart"})


def execute_action(
    action: str,
    speak_fn,
    listen_fn=None,
) -> bool:
    """
    Execute a system-level *action* with an optional security check.

    Parameters
    ----------
    action:
        One of: shutdown, restart, lock, volume_up, volume_down,
        brightness_up, brightness_down.
    speak_fn:
        Callable used for voice feedback.
    listen_fn:
        Callable that returns user speech as a string, used for PIN
        verification.  When ``None`` and a PIN is required, the action
        is blocked.

    Returns
    -------
    bool
        ``True`` if the action was executed, ``False`` if it was blocked.
    """
    if action in DESTRUCTIVE_ACTIONS:
        if not _security_check(action, speak_fn, listen_fn):
            return False

    SystemControl.execute(action, speak_fn=speak_fn)
    return True


def _security_check(action: str, speak_fn, listen_fn) -> bool:
    """
    Verify the user's identity before a destructive action.

    Returns True (allow) when:
    - ``STARK_SECURITY_PIN`` is not set (open mode), OR
    - the user provides the correct PIN via *listen_fn*.

    Returns False (block) when the PIN is wrong or *listen_fn* is None.
    """
    pin = os.getenv("STARK_SECURITY_PIN", "").strip()
    if not pin:
        # No PIN configured — allow (matches current default behaviour)
        return True

    if listen_fn is None:
        speak_fn(
            f"Security PIN is required for '{action}' but no listener is "
            "available.  Action blocked, Sir."
        )
        return False

    speak_fn(
        f"Security check required before '{action}', Sir. "
        "Please say your PIN now."
    )
    provided = listen_fn(timeout=10)
    if provided.replace(" ", "") == pin:
        speak_fn("PIN verified. Proceeding, Sir.")
        return True

    speak_fn("Incorrect PIN. Action cancelled for your security, Sir.")
    return False
