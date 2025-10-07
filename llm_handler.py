"""Back-compat wrappers that forward to finance_ai.llm_handler."""
from finance_ai.llm_handler import (
    MultiModelLLMHandler,
    get_llm_handler,
    is_llm_available,
)

__all__ = [
    "MultiModelLLMHandler",
    "get_llm_handler",
    "is_llm_available",
]
