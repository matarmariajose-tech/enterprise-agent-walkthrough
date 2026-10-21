from functools import lru_cache

from fastapi import Request

from app.adapters.in_memory import (
    InMemoryActionRepository,
    InMemoryAudit,
    InMemoryPayments,
    InMemoryRetrieval,
)
from app.agent.orchestrator import AgentOrchestrator
from app.domain.models import ExecutionContext, Permission
from app.services.authorization import AuthorizationService
from app.services.policy import AlertPolicy, PolicyEngine
from app.tools.payment_tools import PaymentTools


def execution_context(request: Request) -> ExecutionContext:
    return ExecutionContext(
        subject="user:ops_manager",
        tenant="demo:company",
        permissions=frozenset(
            {
                Permission.KNOWLEDGE_INTERNAL,
                Permission.PAYMENTS_READ,
                Permission.ALERTS_PREPARE,
            }
        ),
        trace_id=request.state.trace_id,
        allowed_regions=frozenset({"LATAM"}),
    )


@lru_cache
def orchestrator() -> AgentOrchestrator:
    authorization = AuthorizationService()
    return AgentOrchestrator(
        retrieval=InMemoryRetrieval(),
        payment_tools=PaymentTools(InMemoryPayments(), authorization),
        policy=PolicyEngine(AlertPolicy(version="2026-09", failure_rate_threshold=0.05)),
        authorization=authorization,
        audit=InMemoryAudit(),
        actions=InMemoryActionRepository(),
    )
