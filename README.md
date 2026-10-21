# Enterprise Agent Walkthrough

An interactive architecture case study with a small Python API demonstrating authorization, scoped tools, proposal idempotency and audit traces.

[Open the walkthrough](https://matarmariajose-tech.github.io/enterprise-agent-walkthrough/)

The repository uses fictional data. It contains no client code, credentials or production configuration.

## What runs

| Component | Implemented behavior |
| --- | --- |
| Browser walkthrough | Architecture views, guided tour, details and a repeatable trace simulation |
| FastAPI reference | Validates a request, checks permissions and region scope, reads synthetic evidence and payment statistics, and proposes an alert when the policy threshold is reached |
| Action repository | Atomic proposal creation, conflict detection and tenant/user isolation within one process |
| Action state machine | Pure, version-checked transitions; no approval endpoint or external action executor |
| Audit and tracing | In-memory request events and OpenTelemetry API spans; no telemetry exporter configured |

The browser simulation runs independently from the Python API. It does not call a model or perform external operations. The backend uses LangChain Core for a runnable and a typed tool; it does not implement an MCP server or model-based routing.

## Run the walkthrough

Requires Node.js 22 or newer.

```bash
npm ci
npm run dev
```

The development server prints its local URL. To verify the frontend:

```bash
npm run lint
npm test
npm run build
```

The frontend suite covers the action state machine, repeated simulation runs, concurrent clicks and recovery after rendering errors.

## Run the reference API

Requires Python 3.12 or newer. From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload
```

OpenAPI documentation: `http://localhost:8000/docs`.

```bash
curl http://localhost:8000/v1/health
curl -X POST http://localhost:8000/v1/agent/requests \
  -H 'Content-Type: application/json' \
  -d '{"query":"Review failed payments","region":"LATAM"}'
```

The API deliberately uses a demo identity with LATAM access. Headers cannot grant permissions or change that identity. This is a reference adapter, not production authentication; do not connect private data without replacing it with a validated identity provider.

From `backend/`, verify the API and domain:

```bash
ruff check .
mypy app
pytest
```

The backend suite covers HTTP contracts, permissions, region scope, evidence thresholds, concurrent replays, payload conflicts, identity isolation and inconsistent statistics.

## Request identity and retries

- `correlation_id` identifies a logical request. Send the same UUID to replay it; omitting it creates a new request identifier.
- Proposal keys include tenant, subject and correlation ID. Reusing that key with different request content raises HTTP `409` when creating or retrieving a proposal.
- `trace_id` identifies an individual HTTP attempt and is returned as `X-Request-ID`. A replay gets a new trace while retaining the original proposal.
- Repository results are copied so a caller cannot mutate a stored proposal through a response.

Other classified failures return `403` for denied scope, `422` for invalid input or insufficient evidence, and `503` if a policy is unavailable. Domain errors include the request trace, without echoing the submitted question.

## Structure

```text
src/data/       Reference architecture content and synthetic trace fixtures
src/domain/     Frontend action state machine and types
src/ui/         Walkthrough rendering and interaction controllers
tests/          Frontend behavior tests
backend/app/    API, domain models, services, ports and in-memory adapters
backend/tests/  Domain, concurrency and HTTP tests
docs/           Architecture, limitations and decision records
```

## Scope

This case study demonstrates boundaries, not a deployed enterprise agent. State and audit are in memory, are not durable, and are not shared between worker processes. Proposal idempotency does not provide exactly-once external execution. The state-machine helper does not persist approvals or perform compare-and-swap in a database.

Production identity, document-level retrieval controls, a model, MCP transport, persistent state, external execution and telemetry export are extension points described in [Architecture](docs/architecture.md). GitHub Pages publishes only the static walkthrough; CI checks the frontend and backend separately.

MIT license. See [LICENSE](LICENSE).
