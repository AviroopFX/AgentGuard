"""
Audit log routes for the AgentGuard API.
"""

from fastapi import APIRouter

from agentguard.audit_logger import AuditLogger
from api.models import AuditRecord

router = APIRouter()

audit_logger = AuditLogger()


@router.get("/audit-log", response_model=list[AuditRecord])
def get_audit_log():
    """Return every logged tool call, most recent first."""
    records = audit_logger.list_records()

    # DynamoDB scans don't guarantee order, so sort by timestamp ourselves
    records.sort(key=lambda r: r["timestamp"], reverse=True)

    return records