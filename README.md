# CampaignOps Sentinel

A portfolio-grade, safety-first agentic workflow for gaming-ad operations. It transforms a validated campaign brief into a policy-reviewed inventory recommendation while operating in **Shadow Mode**: the application never creates or changes an external campaign.

## What works now

- FastAPI API with typed campaign brief and approval contracts.
- Deterministic policy review and synthetic inventory connector.
- Shadow-mode recommendation flow with an explicit human-approval endpoint.
- Agent instruction files (`agents/*/SKILL.md`) defining boundaries for future LLM-backed agents.
- Automated tests for normal, invalid, and policy-blocked paths.

## Local setup

```bash
cp .env.example .env
uv sync --all-groups
uv run uvicorn campaign_ops_sentinel.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to try the API.

Run checks:

```bash
uv run ruff check .
uv run pytest
```

## Example request

```bash
curl -X POST http://127.0.0.1:8000/v1/campaigns/recommendations \
  -H 'Content-Type: application/json' \
  -d '{"brand":"Pulse Energy","budget_inr":500000,"markets":["IN"],"audience":"Mobile gamers aged 18 to 30","objective":"attention","start_date":"2026-09-01","end_date":"2026-09-14","formats":["video","playable"],"destination_url":"https://example.com/campaign"}'
```

## Deliberate next additions

1. Replace the synthetic inventory service with a database and an authenticated MCP/REST connector.
2. Add an LLM-backed intake agent behind a provider interface; retain schema validation and policy checks in deterministic code.
3. Persist campaign recommendations, trace IDs, approvals, and audit events in PostgreSQL.
4. Add a dashboard plus evaluation dataset, trace grading, and CI.

## Safety invariants

- Shadow Mode is enabled by default.
- Policy gates are deterministic and run before planning.
- Every external mutation remains unimplemented pending explicit approval, credentials, and integration testing.
- Uploaded brief content must be treated as untrusted data.
