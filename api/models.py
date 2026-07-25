"""
Pydantic models for the AgentGuard API.

These define the shape of data returned by our FastAPI endpoints —
distinct from agentguard/models.py, which defines the internal
dataclasses used by the core library.
"""

from pydantic import BaseModel


class AuditRecord(BaseModel):
    """A single logged tool call, as returned by the API."""

    id: str
    tool_name: str
    agent_id: str
    session_id: str
    arguments: str
    timestamp: str
    decision: str
    risk_level: str
    reason: str


class ApprovalActionResponse(BaseModel):
    """Returned after approving or rejecting a pending action."""

    record_id: str
    status: str
    message: str