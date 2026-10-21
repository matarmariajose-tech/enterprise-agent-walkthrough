import pytest

from app.adapters.in_memory import (
    InMemoryActionRepository,
    InMemoryAudit,
    InMemoryPayments,
    InMemoryRetrieval,
)
from app.agent.orchestrator import AgentOrchestrator
from app.domain.models import AgentRequest, ExecutionContext, Permission
from app.services.authorization import AuthorizationService
from app.services.policy import AlertPolicy, PolicyEngine
from app.tools.payment_tools import PaymentTools


@pytest.mark.asyncio
async def test_proposes_alert_without_executing_side_effect() -> None:
    context = ExecutionContext(
        subject="user:test",
        tenant="LATAM",
        permissions=frozenset(
            {
                Permission.KNOWLEDGE_INTERNAL,
                Permission.PAYMENTS_READ,
                Permission.ALERTS_PREPARE,
            }
        ),
        trace_id="test-trace",
        allowed_regions=frozenset({"LATAM"}),
    )
    authorization = AuthorizationService()
    audit = InMemoryAudit()
    agent = AgentOrchestrator(
        InMemoryRetrieval(),
        PaymentTools(InMemoryPayments(), authorization),
        PolicyEngine(AlertPolicy(version="test", failure_rate_threshold=0.05)),
        authorization,
        audit,
        InMemoryActionRepository(),
    )

    response = await agent.chain.ainvoke(
        (AgentRequest(query="Review failed payments", region="LATAM"), context)
    )

    assert response.action is not None
    assert response.action.status.value == "proposed"
    assert response.action.payload["policy_version"] == "test"
    assert audit.events[0][0] == "agent.request.completed"


@pytest.mark.asyncio
async def test_replay_returns_same_action_without_duplicate_side_effect() -> None:
    context = ExecutionContext(
        subject="user:test",
        tenant="LATAM",
        permissions=frozenset(
            {
                Permission.KNOWLEDGE_INTERNAL,
                Permission.PAYMENTS_READ,
                Permission.ALERTS_PREPARE,
            }
        ),
        trace_id="test-trace",
        allowed_regions=frozenset({"LATAM"}),
    )
    authorization = AuthorizationService()
    actions = InMemoryActionRepository()
    agent = AgentOrchestrator(
        InMemoryRetrieval(),
        PaymentTools(InMemoryPayments(), authorization),
        PolicyEngine(AlertPolicy(version="test", failure_rate_threshold=0.05)),
        authorization,
        InMemoryAudit(),
        actions,
    )
    request = AgentRequest(query="Review failed payments", region="LATAM")

    first = await agent.chain.ainvoke((request, context))
    replay = await agent.chain.ainvoke((request, context))

    assert first.action is not None
    assert replay.action is not None
    assert replay.action.id == first.action.id
