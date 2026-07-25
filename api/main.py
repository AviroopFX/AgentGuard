"""
Main entry point for the AgentGuard API.

Creates the FastAPI app and wires in all route modules.
"""

from dotenv import load_dotenv

load_dotenv()  # MUST run before importing anything that creates AuditLogger

from fastapi import FastAPI

from api.routes import audit

app = FastAPI(
    title="AgentGuard API",
    description="Trust and observability layer for autonomous AI agents.",
    version="0.1.0",
)

app.include_router(audit.router)


@app.get("/")
def root():
    """Simple health check / welcome endpoint."""
    return {"message": "AgentGuard API is running", "docs": "/docs"}