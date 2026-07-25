"""
A LangGraph agent powered by Gemini, using AgentGuard-protected tools.

This demonstrates the full flow: a user gives a natural-language instruction,
the agent decides which tool to call, and AgentGuard evaluates that call
before it's allowed to execute.
"""

import os

from dotenv import load_dotenv

load_dotenv()  # reads GOOGLE_API_KEY from your .env file

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from demo_agent.tools import check_balance, send_email, transfer_funds
from agentguard.middleware import ApprovalRequiredError, ToolBlockedError

load_dotenv()  # reads GOOGLE_API_KEY from your .env file

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=os.environ["GOOGLE_API_KEY"],
)

tools = [check_balance, send_email, transfer_funds]

agent = create_agent(llm, tools)


def run_agent(user_message: str) -> str:
    """Send a message to the agent and return its final response."""
    try:
        result = agent.invoke({"messages": [("user", user_message)]})
        final_message = result["messages"][-1]

        content = final_message.content
        if isinstance(content, list):
            # Newer Gemini responses return a list of content blocks
            content = " ".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            )
        return content

    except ApprovalRequiredError as e:
        return f"⏸ Action paused — requires human approval: {e}"

    except ToolBlockedError as e:
        return f"🚫 Action blocked: {e}"


if __name__ == "__main__":
    print("\n--- Asking agent to check a balance ---")
    print(run_agent("What's the balance of account acc-123?"))

    print("\n--- Asking agent to send an email ---")
    print(run_agent("Send an email to test@example.com with subject 'Hello there'"))

    print("\n--- Asking agent to transfer funds ---")
    print(run_agent("Transfer $500 to external-account"))