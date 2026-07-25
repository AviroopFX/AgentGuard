"""
Audit Logger for AgentGuard.

Persists every PolicyResult to DynamoDB, creating a durable audit trail
of every tool call an agent attempted, and what AgentGuard decided.
"""

import os
import uuid

import boto3

from agentguard.models import PolicyResult


class AuditLogger:
    """Writes PolicyResult records to a DynamoDB table."""

    def __init__(self, table_name: str = "agentguard_audit_log"):
        self._table = boto3.resource(
            "dynamodb",
            region_name=os.environ.get("AWS_REGION", "ap-south-1"),
        ).Table(table_name)

    def log(self, result: PolicyResult) -> str:
        """Write a PolicyResult to DynamoDB. Returns the generated record ID."""
        record_id = str(uuid.uuid4())

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
            }
        )

        return record_id