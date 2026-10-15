import asyncio

from app.domain.models import (
    ActionProposal,
    Evidence,
    ExecutionContext,
    FailureSummary,
    FailureSummaryInput,
    Permission,
)
from app.services.authorization import AuthorizationService


class InMemoryRetrieval:
    async def search(
        self, query: str, context: ExecutionContext, *, limit: int = 4
    ) -> list[Evidence]:
        AuthorizationService.require(context, Permission.KNOWLEDGE_INTERNAL)
        del query, limit
        return [
            Evidence(
                source_id="policy:payments-incident",
                source_version="2026-09",
                excerpt="Prepare a high-priority alert when the 24-hour failure rate reaches 5%.",
                relevance=0.94,
            )
        ]


class InMemoryPayments:
    async def failure_summary(
        self, request: FailureSummaryInput, context: ExecutionContext
    ) -> FailureSummary:
        del request, context
        return FailureSummary(
            total_transactions=10_000,
            failed_transactions=620,
            failure_rate=0.062,
        )


class InMemoryAudit:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict[str, str]]] = []

    async def record(
        self, event: str, context: ExecutionContext, payload: dict[str, str]
    ) -> None:
        self.events.append((event, context.trace_id, payload))


class InMemoryActionRepository:
    """Reference adapter with atomic idempotency semantics.

    A production adapter implements the same contract with a unique database
    constraint on ``idempotency_key`` and a transaction-safe upsert.
    """

    def __init__(self) -> None:
        self._items: dict[str, ActionProposal] = {}
        self._lock = asyncio.Lock()

    async def create_or_get(self, proposal: ActionProposal) -> ActionProposal:
        async with self._lock:
            existing = self._items.get(proposal.idempotency_key)
            if existing is not None:
                return existing
            self._items[proposal.idempotency_key] = proposal
            return proposal
