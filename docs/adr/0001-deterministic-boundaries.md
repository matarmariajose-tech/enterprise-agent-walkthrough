# ADR 0001: Keep business controls outside orchestration

Status: Accepted

## Context

An agent may eventually use a model for intent interpretation. Permissions, resource scope, schemas and business thresholds must remain independently testable when that orchestration changes.

## Decision

Implement authorization, region scope and policy as ordinary Python services behind typed contracts. Bind tool identity per request. The reference orchestrator is deterministic and uses synthetic adapters; adding a model must not bypass those controls.

## Consequences

Negative paths can be tested without a model key or network calls. LangChain stays at the orchestration boundary. MCP transport and model-based routing remain future adapters rather than implied features.
