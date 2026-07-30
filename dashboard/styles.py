"""
Custom CSS for the AgentGuard dashboard.

Streamlit's default look is quite generic, so we inject our own CSS
to get a cleaner, more product-like appearance.
"""

CUSTOM_CSS = """
<style>
    /* Overall page background and font */
    .stApp {
        background-color: #0e1117;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #1c1f26;
        border: 1px solid #2d3139;
        border-radius: 10px;
        padding: 16px;
    }

    /* Section headers */
    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
    }

    /* Risk badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .badge-low {
        background-color: rgba(34, 197, 94, 0.15);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.4);
    }

    .badge-medium {
        background-color: rgba(234, 179, 8, 0.15);
        color: #eab308;
        border: 1px solid rgba(234, 179, 8, 0.4);
    }

    .badge-high {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }

    /* Record cards for pending approvals */
    .record-card {
        background-color: #1c1f26;
        border: 1px solid #2d3139;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }

    .record-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #e5e7eb;
        margin-bottom: 4px;
    }

    .record-meta {
        font-size: 0.85rem;
        color: #9ca3af;
        margin-bottom: 8px;
    }
</style>
"""


def risk_badge(risk_level: str) -> str:
    """Return an HTML badge styled by risk level."""
    return f'<span class="badge badge-{risk_level.lower()}">{risk_level}</span>'