"""
Quick manual test to confirm AuditLogger writes successfully to DynamoDB.
Run with: python test_audit_logger.py
"""

from dotenv import load_dotenv

load_dotenv()  # loads AWS credentials from .env before boto3 needs them

from agentguard.audit_logger import AuditLogger
from agentguard.models import Decision, PolicyResult, RiskLevel, ToolCall

logger = AuditLogger()

tool_call = ToolCall(
    tool_name="transfer_funds",
    arguments={"amount": 500, "to": "external-account"},
    agent_id="agent-001",
    session_id="session-42",
)

result = PolicyResult(
    decision=Decision.NEEDS_APPROVAL,
    risk_level=RiskLevel.HIGH,
    reason="Financial transfer actions require human approval before execution.",
    tool_call=tool_call,
)

record_id = logger.log(result)
print(f"Successfully wrote record to DynamoDB with id: {record_id}")