"""
Approval routes for the AgentGuard API.

Lets a human view pending high-risk actions and approve or reject them.
"""

from fastapi import APIRouter, HTTPException

from agentguard.audit_logger import AuditLogger
from api.models import ApprovalActionResponse, AuditRecord

router = APIRouter()

audit_logger = AuditLogger()


@router.get("/approvals/pending", response_model=list[AuditRecord])
def get_pending_approvals():
    """Return only records that are awaiting human approval."""
    records = audit_logger.list_records()

    pending = [r for r in records if r.get("status") == "pending"]
    pending.sort(key=lambda r: r["timestamp"], reverse=True)

    return pending


@router.post("/approvals/{record_id}/approve", response_model=ApprovalActionResponse)
def approve_record(record_id: str):
    """Approve a pending action."""
    record = audit_logger.get_record(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    if record.get("status") != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Record is not pending approval (current status: {record.get('status')})",
        )

    audit_logger.update_status(record_id, "approved")

    return ApprovalActionResponse(
        record_id=record_id,
        status="approved",
        message=f"Approved '{record['tool_name']}' action for agent {record['agent_id']}.",
    )


@router.post("/approvals/{record_id}/reject", response_model=ApprovalActionResponse)
def reject_record(record_id: str):
    """Reject a pending action."""
    record = audit_logger.get_record(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    if record.get("status") != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Record is not pending approval (current status: {record.get('status')})",
        )

    audit_logger.update_status(record_id, "rejected")

    return ApprovalActionResponse(
        record_id=record_id,
        status="rejected",
        message=f"Rejected '{record['tool_name']}' action for agent {record['agent_id']}.",
    )