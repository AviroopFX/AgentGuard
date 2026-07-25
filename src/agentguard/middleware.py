"""
Middleware for AgentGuard.

Provides a decorator that wraps any tool function, intercepting calls
before they execute, logging them to DynamoDB, and routing them through
the PolicyEngine.
"""

import functools
import logging
from typing import Any, Callable

from agentguard.audit_logger import AuditLogger
from agentguard.models import Decision, PolicyResult, ToolCall
from agentguard.policy_engine import PolicyEngine

logger = logging.getLogger("agentguard")


class ToolBlockedError(Exception):
    """Raised when AgentGuard blocks a tool call outright."""
    pass


class ApprovalRequiredError(Exception):
    """Raised when a tool call needs human approval before it can run."""

    def __init__(self, policy_result: PolicyResult, record_id: str):
        self.policy_result = policy_result
        self.record_id = record_id
        super().__init__(
            f"Tool '{policy_result.tool_call.tool_name}' requires approval: "
            f"{policy_result.reason} (audit record: {record_id})"
        )


class AgentGuard:
    """Main entry point: wraps tool functions with policy enforcement and auditing."""

    def __init__(
        self,
        policy_engine: PolicyEngine | None = None,
        audit_logger: AuditLogger | None = None,
    ):
        self.policy_engine = policy_engine or PolicyEngine()
        self.audit_logger = audit_logger or AuditLogger()

    def protect(self, agent_id: str, session_id: str) -> Callable:
        """
        Decorator that wraps a tool function with risk evaluation and auditing.
        """

        def decorator(tool_fn: Callable) -> Callable:
            @functools.wraps(tool_fn)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                tool_call = ToolCall(
                    tool_name=tool_fn.__name__,
                    arguments=kwargs,
                    agent_id=agent_id,
                    session_id=session_id,
                )

                result = self.policy_engine.evaluate(tool_call)

                # Every evaluated call gets persisted to DynamoDB, regardless of outcome
                record_id = self.audit_logger.log(result)

                logger.info(
                    "Tool call evaluated: tool=%s decision=%s risk=%s record_id=%s",
                    tool_call.tool_name,
                    result.decision,
                    result.risk_level,
                    record_id,
                )

                if result.decision == Decision.BLOCK:
                    raise ToolBlockedError(result.reason)

                if result.decision == Decision.NEEDS_APPROVAL:
                    raise ApprovalRequiredError(result, record_id)

                if result.decision == Decision.FLAG:
                    logger.warning(
                        "Tool call flagged for review: tool=%s reason=%s",
                        tool_call.tool_name,
                        result.reason,
                    )

                return tool_fn(*args, **kwargs)

            return wrapper

        return decorator