import asyncio

import pytest
from conftest import Runtime
from pydantic import ValidationError

from app.domain.errors import (
    AuthorizationError,
    IdempotencyConflictError,
    InsufficientEvidenceError,
)
from app.domain.models import AgentRequest, ExecutionContext, FailureSummary, Permission
from app.services.authorization import AuthorizationService
from app.services.policy import AlertPolicy, PolicyEngine
from app.tools.payment_tools import PaymentTools


@pytest.mark.parametrize(
    "permission",
    [Permission.KNOWLEDGE_INTERNAL, Permission.PAYMENTS_READ, Permission.ALERTS_PREPARE],
)
async def test_denied_permissions_stop_the_request(
    runtime: Runtime, context: ExecutionContext, permission: Permission
) -> None:
    restricted = context.model_copy(update={"permissions": context.permissions - {permission}})
    with pytest.raises(AuthorizationError):
        await runtime.agent().chain.ainvoke(
            (AgentRequest(query="Review payments", region="LATAM"), restricted)
        )
    assert len(runtime.payments.calls) == (1 if permission == Permission.ALERTS_PREPARE else 0)
    assert runtime.audit.events[-1][0] == "agent.request.rejected"


async def test_region_is_checked_before_retrieval(
    runtime: Runtime, context: ExecutionContext
) -> None:
    with pytest.raises(AuthorizationError):
        await runtime.agent().chain.ainvoke(
            (AgentRequest(query="Review payments", region="NA"), context)
        )
    assert not runtime.retrieval.calls
    assert not runtime.payments.calls


async def test_empty_region_scope_fails_closed(runtime: Runtime, context: ExecutionContext) -> None:
    restricted = context.model_copy(update={"allowed_regions": frozenset()})
    with pytest.raises(AuthorizationError):
        await runtime.agent().chain.ainvoke(
            (AgentRequest(query="Review payments", region="LATAM"), restricted)
        )
    assert not runtime.payments.calls


async def test_weak_evidence_does_not_invoke_payments(
    runtime: Runtime, context: ExecutionContext
) -> None:
    runtime.retrieval.evidence = [
        runtime.retrieval.evidence[0].model_copy(update={"relevance": 0.2})
    ]
    with pytest.raises(InsufficientEvidenceError):
        await runtime.agent().chain.ainvoke(
            (AgentRequest(query="Review payments", region="LATAM"), context)
        )
    assert not runtime.payments.calls
    assert runtime.audit.events[-1][0] == "agent.request.rejected"


async def test_below_threshold_does_not_require_prepare_permission(
    runtime: Runtime, context: ExecutionContext
) -> None:
    runtime.payments.summary = FailureSummary(
        total_transactions=100, failed_transactions=1, failure_rate=0.01
    )
    restricted = context.model_copy(
        update={"permissions": context.permissions - {Permission.ALERTS_PREPARE}}
    )
    result = await runtime.agent().chain.ainvoke(
        (AgentRequest(query="Review payments", region="LATAM"), restricted)
    )
    assert result.action is None


@pytest.mark.parametrize("changes", [{"region": "EU"}, {"query": "Different question"}])
async def test_changed_request_cannot_reuse_a_proposal(
    runtime: Runtime, context: ExecutionContext, changes: dict[str, str]
) -> None:
    agent = runtime.agent()
    request = AgentRequest(query="Review payments", region="LATAM")
    await agent.chain.ainvoke((request, context))
    with pytest.raises(IdempotencyConflictError):
        await agent.chain.ainvoke((request.model_copy(update=changes), context))


async def test_concurrent_replays_return_one_proposal(
    runtime: Runtime, context: ExecutionContext
) -> None:
    agent = runtime.agent()
    request = AgentRequest(query="Review payments", region="LATAM")
    responses = await asyncio.gather(*(agent.chain.ainvoke((request, context)) for _ in range(20)))
    assert len({response.action.id for response in responses if response.action}) == 1
    assert all(response.action is not None for response in responses)


@pytest.mark.parametrize("changes", [{"tenant": "other:company"}, {"subject": "other:operator"}])
async def test_proposals_are_scoped_by_tenant_and_subject(
    runtime: Runtime, context: ExecutionContext, changes: dict[str, str]
) -> None:
    agent = runtime.agent()
    request = AgentRequest(query="Review payments", region="LATAM")
    first, other = await asyncio.gather(
        agent.chain.ainvoke((request, context)),
        agent.chain.ainvoke((request, context.model_copy(update=changes))),
    )
    assert first.action and other.action
    assert first.action.id != other.action.id


async def test_response_mutation_cannot_change_stored_proposal(
    runtime: Runtime, context: ExecutionContext
) -> None:
    agent = runtime.agent()
    request = AgentRequest(query="Review payments", region="LATAM")
    first = await agent.chain.ainvoke((request, context))
    assert first.action
    first.action.payload["region"] = "tampered"
    replay = await agent.chain.ainvoke((request, context))
    assert replay.action and replay.action.payload["region"] == "LATAM"


async def test_concurrent_tools_keep_request_identity(
    runtime: Runtime, context: ExecutionContext
) -> None:
    tools = PaymentTools(runtime.payments, AuthorizationService())
    other = context.model_copy(update={"subject": "other", "allowed_regions": frozenset({"EU"})})
    await asyncio.gather(
        tools.for_context(context).ainvoke({"region": "LATAM", "window_hours": 24}),
        tools.for_context(other).ainvoke({"region": "EU", "window_hours": 24}),
    )
    assert {request.region: identity.subject for request, identity in runtime.payments.calls} == {
        "LATAM": context.subject,
        "EU": "other",
    }


async def test_tool_rejects_region_outside_its_bound_context(
    runtime: Runtime, context: ExecutionContext
) -> None:
    tools = PaymentTools(runtime.payments, AuthorizationService())
    with pytest.raises(AuthorizationError):
        await tools.for_context(context).ainvoke({"region": "NA", "window_hours": 24})
    assert not runtime.payments.calls


@pytest.mark.parametrize("total,failed,rate", [(2, 3, 1), (0, 0, 0.1), (100, 5, 0.8)])
def test_inconsistent_payment_statistics_are_rejected(total: int, failed: int, rate: float) -> None:
    with pytest.raises(ValidationError):
        FailureSummary(total_transactions=total, failed_transactions=failed, failure_rate=rate)


@pytest.mark.parametrize("threshold", [-0.1, 1.1, float("nan")])
def test_invalid_policy_thresholds_are_rejected(threshold: float) -> None:
    with pytest.raises(ValueError):
        AlertPolicy(version="test", failure_rate_threshold=threshold)


def test_policy_includes_exact_threshold() -> None:
    policy = PolicyEngine(AlertPolicy(version="test", failure_rate_threshold=0.05))
    assert policy.threshold_exceeded(
        FailureSummary(total_transactions=100, failed_transactions=5, failure_rate=0.05)
    )
