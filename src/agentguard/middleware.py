"""
Middleware for AgentGuard.

Provides a decorator that wraps any tool function, intercepting calls
before they execute and routing them through the PolicyEngine.
"""

import functools
import logging
from typing import Any, Callable

from agentguard.models import Decision, PolicyResult, ToolCall
from agentguard.policy_engine import PolicyEngine

logger = logging.getLogger("agentguard")


class ToolBlockedError(Exception):
    """Raised when AgentGuard blocks a tool call outright."""
    pass


class ApprovalRequiredError(Exception):
    """Raised when a tool call needs human approval before it can run."""

    def __init__(self, policy_result: PolicyResult):
        self.policy_result = policy_result
        super().__init__(
            f"Tool '{policy_result.tool_call.tool_name}' requires approval: "
            f"{policy_result.reason}"
        )


class AgentGuard:
    """Main entry point: wraps tool functions with policy enforcement."""

    def __init__(self, policy_engine: PolicyEngine | None = None):
        self.policy_engine = policy_engine or PolicyEngine()

    def protect(self, agent_id: str, session_id: str) -> Callable:
        """
        Decorator that wraps a tool function with risk evaluation.

        Usage:
            guard = AgentGuard()

            @guard.protect(agent_id="agent-1", session_id="session-1")
            def transfer_funds(amount: float, to: str) -> str:
                return f"Transferred {amount} to {to}"
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
                logger.info(
                    "Tool call evaluated: tool=%s decision=%s risk=%s",
                    tool_call.tool_name,
                    result.decision,
                    result.risk_level,
                )

                if result.decision == Decision.BLOCK:
                    raise ToolBlockedError(result.reason)

                if result.decision == Decision.NEEDS_APPROVAL:
                    raise ApprovalRequiredError(result)

                if result.decision == Decision.FLAG:
                    logger.warning(
                        "Tool call flagged for review: tool=%s reason=%s",
                        tool_call.tool_name,
                        result.reason,
                    )

                # ALLOW or FLAG both proceed to actually run the tool
                return tool_fn(*args, **kwargs)

            return wrapper

        return decorator