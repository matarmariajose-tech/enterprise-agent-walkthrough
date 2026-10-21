# ADR 0002: Separate request tracing and operational state

Status: Accepted

## Context

A retry and its original request belong to the same logical operation but require separate diagnostic traces. Mutable responses must not give callers access to stored proposal state.

## Decision

Use a correlation UUID for logical requests and a new server-generated trace per HTTP attempt. Scope proposal keys by tenant and subject, compare request fingerprints, and return defensive copies. Record completed and rejected requests separately from proposals.

The reference repository uses a process-local lock and in-memory storage. Version checks in the state-machine helper demonstrate the transition contract; they are not a database transaction.

## Consequences

The implementation can test concurrent replays and scope isolation without infrastructure. Durable audit, shared state and atomic versioned updates require a production persistence adapter. No exactly-once execution or conversation storage is claimed.
