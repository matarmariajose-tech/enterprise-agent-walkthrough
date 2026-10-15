# Enterprise Agent Runtime Walkthrough

An interactive, sanitized architecture case study showing how an ambiguous “enterprise chatbot” request can be translated into a governed agent runtime with explicit trust boundaries, typed capabilities, observable execution and controlled side effects.

> This repository contains fictional data and a reconstructed reference architecture. It does not contain client code, credentials, internal documents or production configuration.

## What this demonstrates

- Discovery with nontechnical stakeholders and translation into engineering requirements
- Permission-aware retrieval with evidence provenance
- MCP tools as typed capability boundaries
- Deterministic authorization, validation and side-effect policy
- Versioned action state with explicit approval and idempotency
- Observability as a transversal plane across the full decision path
- Semantic failure analysis beyond availability and HTTP success

## Run locally

```bash
npm install
npm run dev
```

Run the Python API:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

The backend exposes interactive OpenAPI documentation at `http://localhost:8000/docs`.

Quality checks:

```bash
npm run lint
npm test
npm run build
```

## Architecture

The runtime deliberately separates four concerns:

1. **Reasoning** — intent interpretation and capability selection.
2. **Control** — identity, authorization, evidence policy and side-effect decisions.
3. **Execution** — typed MCP capabilities and enterprise APIs.
4. **State and telemetry** — action versions, evidence references, audit events and correlated traces.

See [Architecture](docs/architecture.md) and the [ADRs](docs/adr) for the reasoning behind these boundaries.

## Project structure

```text
src/
  data/       Walkthrough content, trace fixtures and tour configuration
  domain/     Framework-independent types and action state machine
  ui/         Rendering and isolated interaction controllers
tests/        Domain-level behavior tests
docs/         Architecture and decision records
backend/
  app/         FastAPI, LangChain orchestration, domain services and adapters
  tests/       Authorization, state-machine and orchestration behavior tests
```

## Python and LangChain

The backend uses LangChain Core only at the orchestration boundary. Domain policy,
authorization, schemas, action state and integrations remain ordinary Python services.
This keeps the model layer replaceable and prevents framework abstractions from owning
business behavior.

The included adapters are deterministic and contain synthetic data, so the project can
run and test without an API key. A production deployment would provide model, identity,
retrieval, persistence and enterprise API adapters through the same ports.

## Design principles

- Generated values are treated as untrusted input.
- Identity and access scope are resolved before retrieval and tool discovery.
- Existing systems remain authoritative for business data and domain rules.
- Model output cannot directly commit a sensitive side effect.
- Every semantic failure class maps to an explicit control and verification method.

## License

MIT
