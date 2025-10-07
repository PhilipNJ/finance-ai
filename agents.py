"""Back-compat import wrappers for finance_ai.agents.

Prefer importing from the package:
  from finance_ai.agents import AgentWorkflow, ExtractionAgent, OrganizerAgent, DatabaseAgent
"""
from finance_ai.agents import (
    AgentWorkflow,
    ExtractionAgent,
    OrganizerAgent,
    DatabaseAgent,
)

__all__ = [
    "AgentWorkflow",
    "ExtractionAgent",
    "OrganizerAgent",
    "DatabaseAgent",
]
