from __future__ import annotations

import hashlib

from langchain_core.runnables import Runnable, RunnableLambda
from opentelemetry import trace

from app.domain.errors import InsufficientEvidenceError
from app.domain.models import (
    ActionProposal,
    AgentRequest,
    AgentResponse,
    ExecutionContext,
    FailureSummary,
    Permission,
)
from app.ports import ActionRepositoryPort, AuditPort, RetrievalPort
from app.services.authorization import AuthorizationService
from app.services.policy import PolicyEngine
from app.tools.payment_tools import PaymentTools

tracer = trace.get_tracer(__name__)


class AgentOrchestrator:
    """Coordinates model-adjacent reasoning while keeping controls deterministic."""

    def __init__(
        self,
        retrieval: RetrievalPort,
        payment_tools: PaymentTools,
        policy: PolicyEngine,
        authorization: AuthorizationService,
        audit: AuditPort,
        actions: ActionRepositoryPort,
        *,
        minimum_relevance: float = 0.75,
    ) -> None:
        self._retrieval = retrieval
        self._payment_tools = payment_tools
        self._policy = policy
        self._authorization = authorization
        self._audit = audit
        self._actions = actions
        self._minimum_relevance = minimum_relevance
        self.chain: Runnable[
            tuple[AgentRequest, ExecutionContext], AgentResponse
        ] = RunnableLambda[tuple[AgentRequest, ExecutionContext], AgentResponse](self._run)

    async def _run(self, payload: tuple[AgentRequest, ExecutionContext]) -> AgentResponse:
        request, context = payload
        with tracer.start_as_current_span("agent.execute") as span:
            span.set_attribute("agent.trace_id", context.trace_id)
            with tracer.start_as_current_span("retrieval.search"):
                evidence = await self._retrieval.search(request.query, context)
            relevant = [item for item in evidence if item.relevance >= self._minimum_relevance]
            if not relevant:
                raise InsufficientEvidenceError(
                    "No authorized evidence met the relevance threshold"
                )

            tool = self._payment_tools.for_context(context)
            with tracer.start_as_current_span("tool.payments_get_failure_summary"):
                raw_summary = await tool.ainvoke({"region": request.region, "window_hours": 24})
            summary = FailureSummary.model_validate(raw_summary)

            action: ActionProposal | None = None
            if self._policy.threshold_exceeded(summary):
                self._authorization.require(context, Permission.ALERTS_PREPARE)
                digest = hashlib.sha256(
                    f"{context.tenant}:{request.correlation_id}:payment-alert".encode()
                ).hexdigest()
                proposal = ActionProposal(
                    type="publish_operational_alert",
                    idempotency_key=digest,
                    payload={
                        "region": request.region,
                        "policy_version": self._policy.version,
                        "failure_rate": f"{summary.failure_rate:.4f}",
                    },
                )
                action = await self._actions.create_or_get(proposal)

            await self._audit.record(
                "agent.request.completed",
                context,
                {"evidence_count": str(len(relevant)), "action_proposed": str(action is not None)},
            )
            return AgentResponse(
                trace_id=context.trace_id,
                summary=(
                    f"Observed {summary.failed_transactions} failed transactions out of "
                    f"{summary.total_transactions}."
                ),
                evidence=relevant,
                action=action,
            )
