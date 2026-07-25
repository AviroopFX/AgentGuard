"""
Core data models for AgentGuard.

These define the shape of data that flows through the system:
- A ToolCall represents an agent attempting to run a tool.
- A PolicyResult represents the decision AgentGuard makes about that call.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class RiskLevel(str, Enum):
    """How risky a tool call is judged to be."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Decision(str, Enum):
    """What AgentGuard decides to do with a tool call."""
    ALLOW = "allow"              # execute immediately, no issues
    FLAG = "flag"                # execute, but log a warning for review
    BLOCK = "block"              # do not execute, reject outright
    NEEDS_APPROVAL = "needs_approval"  # pause and wait for a human to approve/reject


@dataclass
class ToolCall:
    """Represents a single attempt by an agent to call a tool."""
    tool_name: str
    arguments: dict[str, Any]
    agent_id: str
    session_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PolicyResult:
    """The outcome of evaluating a ToolCall against the policy rules."""
    decision: Decision
    risk_level: RiskLevel
    reason: str
    tool_call: ToolCall