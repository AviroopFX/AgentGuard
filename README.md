# AgentGuard

A trust and observability layer for autonomous AI agents.

## The Problem

Agentic AI adoption is accelerating faster than the governance needed to make it safe. As of 2026, agentic AI governance and autonomous system risk are cited among the top blockers to enterprise AI adoption — teams can build agents that take real actions (send money, delete data, call external APIs) but have little visibility or control over what those agents actually do in production.

## What AgentGuard Does

AgentGuard sits between an AI agent and its tools. Every tool call an agent attempts gets intercepted, scored for risk, and either allowed, flagged, blocked, or paused for human approval — with a full audit trail of every decision.

## Status

🚧 Actively in development. Follow along as this gets built out phase by phase.

## Architecture

*(diagram coming soon)*

## Tech Stack

- Python, FastAPI
- LangGraph
- AWS Bedrock (Claude)
- DynamoDB
- Docker

## Getting Started

*(setup instructions coming as the project develops)*

## License

MIT