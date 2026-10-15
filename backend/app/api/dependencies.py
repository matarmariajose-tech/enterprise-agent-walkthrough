from functools import lru_cache

from app.adapters.in_memory import InMemoryAudit, InMemoryPayments, InMemoryRetrieval
from app.agent.orchestrator import AgentOrchestrator
from app.domain.models import ExecutionContext, Permission
from app.services.authorization import AuthorizationService
from app.services.policy import AlertPolicy, PolicyEngine
from app.tools.payment_tools import PaymentTools


def execution_context() -> ExecutionContext:
    # A production adapter would validate an OIDC token and tenant claims here.
    return ExecutionContext(
        subject="user:ops_manager",
        tenant="LATAM",
        permissions=frozenset(
            {
                Permission.KNOWLEDGE_INTERNAL,
                Permission.PAYMENTS_READ,
                Permission.ALERTS_PREPARE,
            }
        ),
        trace_id="demo_8f21",
    )


@lru_cache
def orchestrator() -> AgentOrchestrator:
    context = execution_context()
    authorization = AuthorizationService()
    return AgentOrchestrator(
        retrieval=InMemoryRetrieval(),
        payment_tools=PaymentTools(InMemoryPayments(), authorization, context),
        policy=PolicyEngine(AlertPolicy(version="2026-09", failure_rate_threshold=0.05)),
        authorization=authorization,
        audit=InMemoryAudit(),
    )
