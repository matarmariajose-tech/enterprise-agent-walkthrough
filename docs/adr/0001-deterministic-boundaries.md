# ADR 0001: Keep business controls outside model reasoning

**Status:** Accepted

## Context

The runtime uses probabilistic reasoning for intent and capability selection. Authorization, schema validation, business thresholds and side-effect commitment require repeatability and independent testing.

## Decision

The model may propose a structured plan. Deterministic services validate permissions, contracts, policy and state transitions before execution.

## Consequences

- Models and prompts can change without redefining business authorization.
- Negative paths can be tested independently from generated language.
- The runtime contains more explicit services and contracts than a direct model-to-API prototype.
