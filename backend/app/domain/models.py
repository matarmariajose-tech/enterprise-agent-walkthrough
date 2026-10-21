from __future__ import annotations

import math
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Region = Literal["LATAM", "EU", "NA"]


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
    allowed_regions: frozenset[Region] = frozenset()


class AgentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: Annotated[str, Field(min_length=3, max_length=4_000)]
    region: Region
    correlation_id: UUID = Field(default_factory=uuid4)


class Evidence(BaseModel, frozen=True):
    source_id: str
    source_version: str
    excerpt: str
    relevance: Annotated[float, Field(ge=0, le=1)]


class FailureSummaryInput(BaseModel, frozen=True):
    region: Region
    window_hours: Literal[1, 6, 24]


class FailureSummary(BaseModel, frozen=True):
    total_transactions: Annotated[int, Field(ge=0)]
    failed_transactions: Annotated[int, Field(ge=0)]
    failure_rate: Annotated[float, Field(ge=0, le=1)]

    @model_validator(mode="after")
    def consistent_totals(self) -> FailureSummary:
        if self.failed_transactions > self.total_transactions:
            raise ValueError("Failed transactions cannot exceed total transactions")
        expected = (
            self.failed_transactions / self.total_transactions if self.total_transactions else 0.0
        )
        if not math.isclose(self.failure_rate, expected, rel_tol=1e-9, abs_tol=1e-12):
            raise ValueError("Failure rate does not match transaction totals")
        return self


class ActionProposal(BaseModel, frozen=True):
    id: UUID = Field(default_factory=uuid4)
    type: Literal["publish_operational_alert"]
    status: ActionStatus = ActionStatus.PROPOSED
    version: Annotated[int, Field(ge=1)] = 1
    idempotency_key: str
    request_fingerprint: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    payload: dict[str, str]


class AgentResponse(BaseModel):
    trace_id: str
    summary: str
    evidence: list[Evidence]
    action: ActionProposal | None = None
