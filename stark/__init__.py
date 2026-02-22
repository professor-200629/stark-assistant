"""
stark – Personal AI Operating System package.

Public API
----------
StarkAssistant
    The main assistant class (see stark.core).
speak
    Text-to-speech helper (see stark.voice).
listen
    Speech-recognition helper (see stark.voice).

Quick start
-----------
>>> from stark import StarkAssistant
>>> assistant = StarkAssistant()
>>> assistant.process_command("what time is it")

Entry point
-----------
Run ``python -m stark`` to start the interactive voice loop.
"""

from .core import StarkAssistant
from .voice import listen, speak

__all__ = ["StarkAssistant", "speak", "listen"]
