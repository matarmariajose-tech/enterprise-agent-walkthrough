# ADR 0002: Separate telemetry, conversation history and action state

**Status:** Accepted

## Context

Chat transcripts do not provide enough structure to diagnose semantic failures or guarantee safe side effects.

## Decision

- Observability is a transversal plane using correlated structured spans.
- Conversation history is stored for continuity.
- Action state is versioned and persisted transactionally with evidence and audit references.

## Consequences

- A request can be reconstructed across service boundaries.
- Stale approvals and duplicate actions can be rejected.
- Sensitive telemetry requires explicit redaction and retention rules.
