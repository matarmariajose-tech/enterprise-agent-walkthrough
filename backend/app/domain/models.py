from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Permission(StrEnum):
    KNOWLEDGE_INTERNAL = "knowledge:internal"
    PAYMENTS_READ = "payments:read"
    ALERTS_PREPARE = "alerts:prepare"
    ALERTS_PUBLISH = "alerts:publish"


class ActionStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionContext(BaseModel, frozen=True):
    subject: str
    tenant: str
    permissions: frozenset[Permission]
    trace_id: str


class AgentRequest(BaseModel):
    query: Annotated[str, Field(min_length=3, max_length=4_000)]
    region: Literal["LATAM", "EU", "NA"]
    correlation_id: UUID = Field(default_factory=uuid4)


class Evidence(BaseModel, frozen=True):
    source_id: str
    source_version: str
    excerpt: str
    relevance: Annotated[float, Field(ge=0, le=1)]


class FailureSummaryInput(BaseModel, frozen=True):
    region: Literal["LATAM", "EU", "NA"]
    window_hours: Literal[1, 6, 24]


class FailureSummary(BaseModel, frozen=True):
    total_transactions: Annotated[int, Field(ge=0)]
    failed_transactions: Annotated[int, Field(ge=0)]
    failure_rate: Annotated[float, Field(ge=0, le=1)]


class ActionProposal(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["publish_operational_alert"]
    status: ActionStatus = ActionStatus.PROPOSED
    version: Annotated[int, Field(ge=1)] = 1
    idempotency_key: str
    payload: dict[str, str]


class AgentResponse(BaseModel):
    trace_id: str
    summary: str
    evidence: list[Evidence]
    action: ActionProposal | None = None
