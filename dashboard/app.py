"""
AgentGuard Dashboard.

A Streamlit UI for viewing the audit trail and managing pending approvals,
built on top of the AgentGuard FastAPI backend.
"""

import requests
import streamlit as st

from styles import CUSTOM_CSS, risk_badge

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AgentGuard Dashboard",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def fetch_audit_log() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/audit-log")
    response.raise_for_status()
    return response.json()


def fetch_pending_approvals() -> list[dict]:
    response = requests.get(f"{API_BASE_URL}/approvals/pending")
    response.raise_for_status()
    return response.json()


def approve_record(record_id: str) -> None:
    response = requests.post(f"{API_BASE_URL}/approvals/{record_id}/approve")
    response.raise_for_status()


def reject_record(record_id: str) -> None:
    response = requests.post(f"{API_BASE_URL}/approvals/{record_id}/reject")
    response.raise_for_status()


# ---------- Header ----------

st.title("🛡️ AgentGuard")
st.caption("Trust and observability layer for autonomous AI agents")

# ---------- Data fetch ----------

try:
    audit_log = fetch_audit_log()
    pending = fetch_pending_approvals()
except requests.exceptions.ConnectionError:
    st.error(
        "Could not connect to the AgentGuard API. "
        "Make sure it's running: `uvicorn api.main:app --reload`"
    )
    st.stop()

# ---------- Metrics row ----------

total_calls = len(audit_log)
high_risk_count = sum(1 for r in audit_log if r["risk_level"] == "high")
pending_count = len(pending)

col1, col2, col3 = st.columns(3)
col1.metric("Total Tool Calls", total_calls)
col2.metric("High Risk Calls", high_risk_count)
col3.metric("Pending Approvals", pending_count)

st.divider()

# ---------- Pending approvals section ----------

st.subheader("⏸ Pending Approvals")

if not pending:
    st.info("No actions currently awaiting approval.")
else:
    for record in pending:
        with st.container():
            st.markdown(
                f"""
                <div class="record-card">
                    <div class="record-title">{record['tool_name']}</div>
                    <div class="record-meta">
                        Agent: {record['agent_id']} • Session: {record['session_id']}<br>
                        Arguments: {record['arguments']}<br>
                        {risk_badge(record['risk_level'])}
                    </div>
                    <div class="record-meta">{record['reason']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn_col1, btn_col2, _ = st.columns([1, 1, 4])

            with btn_col1:
                if st.button("✅ Approve", key=f"approve-{record['id']}"):
                    approve_record(record["id"])
                    st.rerun()

            with btn_col2:
                if st.button("❌ Reject", key=f"reject-{record['id']}"):
                    reject_record(record["id"])
                    st.rerun()

st.divider()

# ---------- Full audit log ----------

st.subheader("📋 Full Audit Log")

for record in audit_log:
    st.markdown(
        f"""
        <div class="record-card">
            <div class="record-title">{record['tool_name']} {risk_badge(record['risk_level'])}</div>
            <div class="record-meta">
                {record['timestamp']} • Agent: {record['agent_id']} • Decision: {record['decision']}
            </div>
            <div class="record-meta">{record['reason']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )