# 🛡️ AgentGuard

**A trust and observability layer for autonomous AI agents.**

AgentGuard sits between an AI agent and its tools — intercepting every tool call, scoring it for risk, and enforcing what happens next: allow it, flag it for review, block it outright, or pause it for human approval. Every decision is permanently logged to a cloud audit trail.

---

## The Problem

Agentic AI adoption is accelerating faster than the governance needed to make it safe. Enterprise surveys consistently cite agentic AI governance and autonomous system risk among the top blockers to production AI adoption in 2026 — teams can build agents that take real actions (transfer money, delete records, call external APIs), but have little visibility or control over what those agents actually do once deployed.

Most guardrail solutions on the market today are heavyweight, ML-classifier-based enterprise platforms. AgentGuard is the foundational *pattern* underneath them: rule-based policy enforcement, audit logging, and human-in-the-loop approval — simple enough to fully understand, real enough to actually run.

## What AgentGuard Does

- **Intercepts** every tool call an agent attempts, before it executes
- **Scores risk** against a configurable policy (`rules.yaml`) — no code changes needed to adjust what's considered risky
- **Enforces a decision**: `ALLOW` (runs immediately), `FLAG` (runs, logged for review), `BLOCK` (never runs), or `NEEDS_APPROVAL` (paused until a human acts)
- **Logs everything** to DynamoDB — a permanent, queryable audit trail of every attempted action, resolved or not
- **Exposes an API and dashboard** so a human can review pending high-risk actions and approve or reject them in real time

## Demo

**Dashboard** — live view of tool calls, risk levels, and pending approvals:

*(insert dashboard screenshot here)*

**Pending approval with real-time metrics:**

*(insert metrics screenshot here)*

## Architecture

```
┌──────────────────┐
│  LangGraph Agent   │  (Gemini-powered demo agent with 3 tools)
└─────────┬──────────┘
          │ tool call attempt
          ▼
┌───────────────────────────────────────┐
│           AgentGuard Middleware          │
│  ┌───────────────┐   ┌────────────────┐ │
│  │ Policy Engine   │→ │ Decision:       │ │
│  │ (rules.yaml)    │   │ allow / flag /  │ │
│  │                 │   │ block / approve │ │
│  └───────────────┘   └────────────────┘ │
└─────────┬─────────────────────┬─────────┘
          │                     │
          ▼                     ▼
┌──────────────────┐   ┌──────────────────┐
│  DynamoDB Audit    │   │  FastAPI Backend   │
│  Log (every call)  │   │  /audit-log         │
│                    │   │  /approvals/pending  │
│                    │   │  /approvals/{id}/... │
└──────────────────┘   └─────────┬────────┘
                                   │
                                   ▼
                        ┌──────────────────┐
                        │ Streamlit Dashboard│
                        │ (view + approve)   │
                        └──────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Agent framework | LangGraph, LangChain |
| LLM | Google Gemini (`gemini-3.5-flash-lite`) |
| Backend API | FastAPI |
| Audit storage | AWS DynamoDB |
| Dashboard | Streamlit |
| Containerization | Docker, Docker Compose |
| Testing | pytest (14 tests — policy engine, middleware, approval API) |

**Roadmap note:** built with Gemini as the LLM provider due to AWS Bedrock's new-account use-case approval process; the architecture is provider-agnostic, and swapping in Bedrock (Claude/Titan) is a contained change to the LLM client, not the agent or middleware logic. Migrating to Bedrock is a near-term next step.

## Getting Started

### Option A: Docker (recommended — one command)

```bash
git clone https://github.com/YOUR-USERNAME/AgentGuard.git
cd AgentGuard
cp .env.example .env   # then fill in your own API keys — see below
docker compose up --build
```

- API docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501

**First run?** The dashboard starts empty — no data exists until an agent actually makes tool calls. In a separate terminal, run:
```bash
docker compose exec api python -m demo_agent.agent
```
Then refresh the dashboard to see real activity: an allowed call, a flagged call, and a pending approval.

### Option B: Local (manual)

```bash
git clone https://github.com/YOUR-USERNAME/AgentGuard.git
cd AgentGuard
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install -e .
cp .env.example .env   # then fill in your own API keys

# Terminal 1
uvicorn api.main:app --reload

# Terminal 2
streamlit run dashboard/app.py

# Terminal 3 — run the demo agent (this is what populates the dashboard with data)
python -m demo_agent.agent
```

### Environment variables (`.env`)

```
GOOGLE_API_KEY=your-gemini-api-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=your-aws-region
```

You'll also need a DynamoDB table named `agentguard_audit_log` with a partition key `id` (String) in your AWS account.

### Running tests

```bash
pytest -v
```

## Project Structure

```
agentguard/
├── src/agentguard/     # Core library: policy engine, middleware, audit logger
├── demo_agent/          # LangGraph agent demonstrating AgentGuard in use
├── api/                 # FastAPI backend (audit log + approval endpoints)
├── dashboard/            # Streamlit dashboard
├── tests/                # pytest suite
├── Dockerfile
├── docker-compose.yml
```

## What's Next

- Migrate LLM provider from Gemini to AWS Bedrock (Claude)
- Full agent resumption after approval (LangGraph checkpointing/persistence)
- LLM-as-judge risk scoring, as an alternative to static rules

## License

MIT