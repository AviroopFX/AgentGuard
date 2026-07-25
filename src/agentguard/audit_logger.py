"""
Audit Logger for AgentGuard.

Persists every PolicyResult to DynamoDB, creating a durable audit trail
of every tool call an agent attempted, and what AgentGuard decided.
"""

import os
import uuid

import boto3

from agentguard.models import Decision, PolicyResult


class AuditLogger:
    """Writes and reads PolicyResult records from a DynamoDB table."""

    def __init__(self, table_name: str = "agentguard_audit_log"):
        self._table = boto3.resource(
            "dynamodb",
            region_name=os.environ.get("AWS_REGION", "ap-south-1"),
        ).Table(table_name)

    def log(self, result: PolicyResult) -> str:
        """Write a PolicyResult to DynamoDB. Returns the generated record ID."""
        record_id = str(uuid.uuid4())

        # Only NEEDS_APPROVAL calls start life as "pending" — everything else
        # is already resolved the moment it's logged.
        status = "pending" if result.decision == Decision.NEEDS_APPROVAL else "resolved"

        self._table.put_item(
            Item={
                "id": record_id,
                "tool_name": result.tool_call.tool_name,
                "agent_id": result.tool_call.agent_id,
                "session_id": result.tool_call.session_id,
                "arguments": str(result.tool_call.arguments),
                "timestamp": result.tool_call.timestamp.isoformat(),
                "decision": result.decision.value,
                "risk_level": result.risk_level.value,
                "reason": result.reason,
                "status": status,
            }
        )

        return record_id

    def list_records(self) -> list[dict]:
        """Retrieve all audit records from DynamoDB."""
        response = self._table.scan()
        return response.get("Items", [])

    def get_record(self, record_id: str) -> dict | None:
        """Retrieve a single record by its id. Returns None if not found."""
        response = self._table.get_item(Key={"id": record_id})
        return response.get("Item")

    def update_status(self, record_id: str, new_status: str) -> None:
        """Update the status field of an existing record (e.g. 'approved', 'rejected')."""
        self._table.update_item(
            Key={"id": record_id},
            UpdateExpression="SET #s = :new_status",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":new_status": new_status},
        )