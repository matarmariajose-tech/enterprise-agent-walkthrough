from __future__ import annotations

from langchain_core.tools import StructuredTool

from app.domain.models import ExecutionContext, FailureSummary, FailureSummaryInput, Permission
from app.ports import PaymentsPort
from app.services.authorization import AuthorizationService


class PaymentTools:
    def __init__(
        self,
        payments: PaymentsPort,
        authorization: AuthorizationService,
    ) -> None:
        self._payments = payments
        self._authorization = authorization

    def for_context(self, context: ExecutionContext) -> StructuredTool:
        """Bind identity at request scope; never retain it on the singleton registry."""

        async def get_failure_summary(region: str, window_hours: int) -> dict[str, int | float]:
            self._authorization.require(context, Permission.PAYMENTS_READ)
            request = FailureSummaryInput.model_validate(
                {"region": region, "window_hours": window_hours}
            )
            self._authorization.require_region(context, request.region)
            result: FailureSummary = await self._payments.failure_summary(request, context)
            return result.model_dump()

        return StructuredTool.from_function(
            coroutine=get_failure_summary,
            name="payments_get_failure_summary",
            description=(
                "Return aggregate payment failure statistics for an authorized region and "
                "bounded time window. This tool is read-only and never exposes customer data."
            ),
            args_schema=FailureSummaryInput,
        )
