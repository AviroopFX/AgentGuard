"""
Main entry point for the AgentGuard API.

Creates the FastAPI app and wires in all route modules.
"""

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from api.routes import approvals, audit

app = FastAPI(
    title="AgentGuard API",
    description="Trust and observability layer for autonomous AI agents.",
    version="0.1.0",
)

app.include_router(audit.router)
app.include_router(approvals.router)


@app.get("/")
def root():
    """Simple health check / welcome endpoint."""
    return {"message": "AgentGuard API is running", "docs": "/docs"}