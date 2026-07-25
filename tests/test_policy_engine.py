"""
Tests for the PolicyEngine.

Verifies that tool calls are correctly evaluated against rules.yaml,
including the fallback behavior for unknown tools.
"""

import pytest

from agentguard.models import Decision, RiskLevel, ToolCall
from agentguard.policy_engine import PolicyEngine


@pytest.fixture
def engine() -> PolicyEngine:
    """Creates a fresh PolicyEngine before each test."""
    return PolicyEngine()


def test_low_risk_tool_is_allowed(engine: PolicyEngine):
    tool_call = ToolCall(
        tool_name="check_balance",
        arguments={"account_id": "acc-123"},
        agent_id="agent-1",
        session_id="session-1",
    )

    result = engine.evaluate(tool_call)

    assert result.decision == Decision.ALLOW
    assert result.risk_level == RiskLevel.LOW


def test_high_risk_tool_needs_approval(engine: PolicyEngine):
    tool_call = ToolCall(
        tool_name="transfer_funds",
        arguments={"amount": 500, "to": "external-account"},
        agent_id="agent-1",
        session_id="session-1",
    )

    result = engine.evaluate(tool_call)

    assert result.decision == Decision.NEEDS_APPROVAL
    assert result.risk_level == RiskLevel.HIGH


def test_medium_risk_tool_is_flagged(engine: PolicyEngine):
    tool_call = ToolCall(
        tool_name="send_email",
        arguments={"to": "test@example.com", "subject": "Hello"},
        agent_id="agent-1",
        session_id="session-1",
    )

    result = engine.evaluate(tool_call)

    assert result.decision == Decision.FLAG
    assert result.risk_level == RiskLevel.MEDIUM


def test_unknown_tool_falls_back_to_default(engine: PolicyEngine):
    tool_call = ToolCall(
        tool_name="some_new_tool_nobody_configured",
        arguments={},
        agent_id="agent-1",
        session_id="session-1",
    )

    result = engine.evaluate(tool_call)

    # Falls back to the "default" block in rules.yaml
    assert result.decision == Decision.FLAG
    assert result.risk_level == RiskLevel.MEDIUM


def test_policy_result_carries_original_tool_call(engine: PolicyEngine):
    tool_call = ToolCall(
        tool_name="check_balance",
        arguments={"account_id": "acc-123"},
        agent_id="agent-1",
        session_id="session-1",
    )

    result = engine.evaluate(tool_call)

    # The result should preserve the exact tool_call that was evaluated
    assert result.tool_call.tool_name == "check_balance"
    assert result.tool_call.agent_id == "agent-1"