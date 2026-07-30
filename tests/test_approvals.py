"""
Tests for the approval routes.

Uses a fake AuditLogger and FastAPI's TestClient so these tests run
fast, offline, and never touch real DynamoDB.
"""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.routes import approvals


class FakeAuditLogger:
    """A stand-in for AuditLogger, backed by an in-memory dictionary."""

    def __init__(self):
        self.records: dict[str, dict] = {}

    def seed(self, record_id: str, **fields):
        """Test helper: directly insert a record, bypassing .log()."""
        self.records[record_id] = {"id": record_id, **fields}

    def list_records(self) -> list[dict]:
        return list(self.records.values())

    def get_record(self, record_id: str) -> dict | None:
        return self.records.get(record_id)

    def update_status(self, record_id: str, new_status: str) -> None:
        self.records[record_id]["status"] = new_status


@pytest.fixture
def fake_logger() -> FakeAuditLogger:
    return FakeAuditLogger()


@pytest.fixture
def client(fake_logger: FakeAuditLogger) -> TestClient:
    """A TestClient with the real audit_logger swapped for our fake."""
    approvals.audit_logger = fake_logger
    return TestClient(app)


def test_pending_approvals_returns_only_pending_records(
    client: TestClient, fake_logger: FakeAuditLogger
):
    fake_logger.seed(
        "record-1",
        tool_name="transfer_funds",
        agent_id="agent-1",
        session_id="session-1",
        arguments="{}",
        timestamp="2026-01-01T00:00:00+00:00",
        decision="needs_approval",
        risk_level="high",
        reason="test",
        status="pending",
    )
    fake_logger.seed(
        "record-2",
        tool_name="check_balance",
        agent_id="agent-1",
        session_id="session-1",
        arguments="{}",
        timestamp="2026-01-01T00:00:01+00:00",
        decision="allow",
        risk_level="low",
        reason="test",
        status="resolved",
    )

    response = client.get("/approvals/pending")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "record-1"


def test_approve_pending_record_succeeds(client: TestClient, fake_logger: FakeAuditLogger):
    fake_logger.seed(
        "record-1",
        tool_name="transfer_funds",
        agent_id="agent-1",
        session_id="session-1",
        arguments="{}",
        timestamp="2026-01-01T00:00:00+00:00",
        decision="needs_approval",
        risk_level="high",
        reason="test",
        status="pending",
    )

    response = client.post("/approvals/record-1/approve")

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert fake_logger.get_record("record-1")["status"] == "approved"


def test_approve_nonexistent_record_returns_404(client: TestClient):
    response = client.post("/approvals/does-not-exist/approve")

    assert response.status_code == 404


def test_approve_already_resolved_record_returns_400(
    client: TestClient, fake_logger: FakeAuditLogger
):
    fake_logger.seed(
        "record-1",
        tool_name="transfer_funds",
        agent_id="agent-1",
        session_id="session-1",
        arguments="{}",
        timestamp="2026-01-01T00:00:00+00:00",
        decision="needs_approval",
        risk_level="high",
        reason="test",
        status="approved",  # already resolved
    )

    response = client.post("/approvals/record-1/approve")

    assert response.status_code == 400