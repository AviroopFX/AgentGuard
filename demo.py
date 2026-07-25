"""
Quick manual test to see AgentGuard working end-to-end.
Run this with: python demo.py
"""

from agentguard.middleware import AgentGuard, ToolBlockedError, ApprovalRequiredError
import logging
logging.basicConfig(level=logging.INFO)

guard = AgentGuard()


@guard.protect(agent_id="agent-001", session_id="session-42")
def check_balance(account_id: str) -> str:
    return f"Balance for {account_id}: $1,200"


@guard.protect(agent_id="agent-001", session_id="session-42")
def send_email(to: str, subject: str) -> str:
    return f"Email sent to {to} with subject '{subject}'"


@guard.protect(agent_id="agent-001", session_id="session-42")
def transfer_funds(amount: float, to: str) -> str:
    return f"Transferred {amount} to {to}"


if __name__ == "__main__":
    # LOW risk — should just work
    print("\n--- Testing check_balance (should ALLOW) ---")
    result = check_balance(account_id="acc-123")
    print(result)

    # MEDIUM risk — should work but log a warning
    print("\n--- Testing send_email (should FLAG) ---")
    result = send_email(to="test@example.com", subject="Hello")
    print(result)

    # HIGH risk — should raise an error, requiring approval
    print("\n--- Testing transfer_funds (should NEEDS_APPROVAL) ---")
    try:
        result = transfer_funds(amount=500, to="external-account")
        print(result)
    except ApprovalRequiredError as e:
        print(f"BLOCKED (needs approval): {e}")