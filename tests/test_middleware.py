"""
Tests for the AgentGuard middleware decorator.

Uses a fake AuditLogger so tests don't hit real AWS/DynamoDB.
"""

import pytest

from agentguard.middleware import AgentGuard, ApprovalRequiredError, ToolBlockedError
from agentguard.models import PolicyResult


class FakeAuditLogger:
    """A stand-in for AuditLogger that just stores records in memory."""

    def __init__(self):
        self.logged_results: list[PolicyResult] = []

    def log(self, result: PolicyResult) -> str:
        self.logged_results.append(result)
        return f"fake-record-{len(self.logged_results)}"


@pytest.fixture
def fake_audit_logger() -> FakeAuditLogger:
    return FakeAuditLogger()


@pytest.fixture
def guard(fake_audit_logger: FakeAuditLogger) -> AgentGuard:
    return AgentGuard(audit_logger=fake_audit_logger)


def test_low_risk_tool_executes_normally(guard: AgentGuard):
    @guard.protect(agent_id="agent-1", session_id="session-1")
    def check_balance(account_id: str) -> str:
        return f"Balance for {account_id}: $1,200"

    result = check_balance(account_id="acc-123")

    assert result == "Balance for acc-123: $1,200"


def test_high_risk_tool_raises_approval_required(guard: AgentGuard):
    @guard.protect(agent_id="agent-1", session_id="session-1")
    def transfer_funds(amount: float, to: str) -> str:
        return f"Transferred {amount} to {to}"

    with pytest.raises(ApprovalRequiredError):
        transfer_funds(amount=500, to="external-account")


def test_blocked_tool_never_executes(guard: AgentGuard):
    call_tracker = {"executed": False}

    @guard.protect(agent_id="agent-1", session_id="session-1")
    def transfer_funds(amount: float, to: str) -> str:
        call_tracker["executed"] = True
        return f"Transferred {amount} to {to}"

    with pytest.raises(ApprovalRequiredError):
        transfer_funds(amount=500, to="external-account")

    # The real function body should NEVER have run
    assert call_tracker["executed"] is False


def test_every_call_gets_audited(guard: AgentGuard, fake_audit_logger: FakeAuditLogger):
    @guard.protect(agent_id="agent-1", session_id="session-1")
    def check_balance(account_id: str) -> str:
        return f"Balance for {account_id}: $1,200"

    check_balance(account_id="acc-123")

    assert len(fake_audit_logger.logged_results) == 1
    assert fake_audit_logger.logged_results[0].tool_call.tool_name == "check_balance"


def test_approval_error_carries_record_id(guard: AgentGuard):
    @guard.protect(agent_id="agent-1", session_id="session-1")
    def transfer_funds(amount: float, to: str) -> str:
        return f"Transferred {amount} to {to}"

    with pytest.raises(ApprovalRequiredError) as exc_info:
        transfer_funds(amount=500, to="external-account")

    assert exc_info.value.record_id == "fake-record-1"