"""Script Generation Package.

This package provides comprehensive script generation capabilities with
time allocation, language adaptation, and quality control.
"""

from .script_engine import (
    ScriptEngine,
    ScriptSection,
    GeneratedScript
)
from .time_allocator import (
    TimeAllocator,
    TimeAllocation
)
from .language_adapter import (
    LanguageAdapter,
    ScriptTemplate
)

__all__ = [
    "ScriptEngine",
    "ScriptSection",
    "GeneratedScript",
    "TimeAllocator",
    "TimeAllocation",
    "LanguageAdapter",
    "LanguageProfile",
    "AdaptedContent",
]
