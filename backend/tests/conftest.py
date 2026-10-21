import asyncio
from dataclasses import dataclass, field

import pytest

from app.adapters.in_memory import InMemoryActionRepository, InMemoryAudit
from app.agent.orchestrator import AgentOrchestrator
from app.domain.models import (
    Evidence,
    ExecutionContext,
    FailureSummary,
    FailureSummaryInput,
    Permission,
)
from app.services.authorization import AuthorizationService
from app.services.policy import AlertPolicy, PolicyEngine
from app.tools.payment_tools import PaymentTools


@dataclass
class RecordingRetrieval:
    evidence: list[Evidence] = field(
        default_factory=lambda: [
            Evidence(
                source_id="test-policy",
                source_version="1",
                excerpt="Synthetic policy",
                relevance=0.9,
            )
        ]
    )
    calls: list[ExecutionContext] = field(default_factory=list)

    async def search(
        self, query: str, context: ExecutionContext, *, limit: int = 4
    ) -> list[Evidence]:
        self.calls.append(context)
        return self.evidence[:limit]


@dataclass
class RecordingPayments:
    summary: FailureSummary = field(
        default_factory=lambda: FailureSummary(
            total_transactions=100, failed_transactions=6, failure_rate=0.06
        )
    )
    calls: list[tuple[FailureSummaryInput, ExecutionContext]] = field(default_factory=list)

    async def failure_summary(
        self, request: FailureSummaryInput, context: ExecutionContext
    ) -> FailureSummary:
        self.calls.append((request, context))
        await asyncio.sleep(0)
        return self.summary


@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext(
        subject="test:operator",
        tenant="test:company",
        trace_id="test-trace",
        permissions=frozenset(
            {Permission.KNOWLEDGE_INTERNAL, Permission.PAYMENTS_READ, Permission.ALERTS_PREPARE}
        ),
        allowed_regions=frozenset({"LATAM", "EU"}),
    )


@dataclass
class Runtime:
    retrieval: RecordingRetrieval = field(default_factory=RecordingRetrieval)
    payments: RecordingPayments = field(default_factory=RecordingPayments)
    audit: InMemoryAudit = field(default_factory=InMemoryAudit)
    actions: InMemoryActionRepository = field(default_factory=InMemoryActionRepository)

    def agent(self) -> AgentOrchestrator:
        authorization = AuthorizationService()
        return AgentOrchestrator(
            self.retrieval,
            PaymentTools(self.payments, authorization),
            PolicyEngine(AlertPolicy(version="test", failure_rate_threshold=0.05)),
            authorization,
            self.audit,
            self.actions,
        )


@pytest.fixture
def runtime() -> Runtime:
    return Runtime()
