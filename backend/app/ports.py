from __future__ import annotations

from typing import Protocol

from app.domain.models import (
    Evidence,
    ExecutionContext,
    FailureSummary,
    FailureSummaryInput,
)


class RetrievalPort(Protocol):
    async def search(
        self, query: str, context: ExecutionContext, *, limit: int = 4
    ) -> list[Evidence]: ...


class PaymentsPort(Protocol):
    async def failure_summary(
        self, request: FailureSummaryInput, context: ExecutionContext
    ) -> FailureSummary: ...


class AuditPort(Protocol):
    async def record(
        self, event: str, context: ExecutionContext, payload: dict[str, str]
    ) -> None: ...
