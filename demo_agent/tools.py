"""
Tools for the demo LangGraph agent.

Each tool is wrapped with AgentGuard's @protect decorator, so every call
the agent makes gets evaluated against our risk rules before it executes.
"""

from langchain_core.tools import tool

from agentguard.middleware import AgentGuard

guard = AgentGuard()

AGENT_ID = "demo-langgraph-agent"
SESSION_ID = "demo-session-1"


@tool
@guard.protect(agent_id=AGENT_ID, session_id=SESSION_ID)
def check_balance(account_id: str) -> str:
    """Check the current balance of a given account ID."""
    return f"Balance for {account_id}: $1,200"


@tool
@guard.protect(agent_id=AGENT_ID, session_id=SESSION_ID)
def send_email(to: str, subject: str) -> str:
    """Send an email to a recipient with a given subject."""
    return f"Email sent to {to} with subject '{subject}'"


@tool
@guard.protect(agent_id=AGENT_ID, session_id=SESSION_ID)
def transfer_funds(amount: float, to: str) -> str:
    """Transfer a specified amount of money to a recipient account."""
    return f"Transferred {amount} to {to}"