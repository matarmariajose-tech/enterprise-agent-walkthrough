# Architecture

## Problem framing

The initial product language described a chatbot. Discovery exposed a broader system:

- multiple actor types with different resource scopes;
- internal knowledge with tenant and document-level access constraints;
- reports, alerts and operations in existing systems;
- conversational continuity plus durable operational state;
- semantic reliability requirements that normal infrastructure metrics cannot measure.

## Runtime boundaries

### Orchestration

The model interprets intent and selects from an allowlisted capability set. It does not own authorization, validation, business thresholds or side-effect commitment.

### Retrieval

Access control is applied before ranking. Results retain source identity and version so generated statements can be connected to the exact evidence used.

### Tool execution

MCP tools expose narrow business capabilities. Their contracts declare permissions, typed input, typed output, timeout budget, retry classification and side-effect behavior.

### Action lifecycle

Side effects use a versioned state machine:

```text
idle → proposed → approved → executing → completed | failed
```

At-least-once delivery requires idempotent consumers. Stale approvals and duplicate executions are rejected.

### Observability

Telemetry is a transversal plane rather than a step in the business decision. Structured spans connect identity, retrieval, routing, validation, API results, policy decisions and action state through a correlation id.

### State

Conversation messages support continuity. Operational state separately stores evidence references, action versions, approval identity, idempotency keys and immutable audit events.

## Failure model

The most important failure class is semantic: a technically successful request with insufficient evidence or incorrect routing. The diagnostic process reconstructs the entire decision path before selecting a remediation.
