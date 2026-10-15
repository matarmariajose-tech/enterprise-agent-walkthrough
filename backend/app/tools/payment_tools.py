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
        context: ExecutionContext,
    ) -> None:
        self._payments = payments
        self._authorization = authorization
        self._context = context

    async def get_failure_summary(
        self, region: str, window_hours: int
    ) -> dict[str, int | float]:
        self._authorization.require(self._context, Permission.PAYMENTS_READ)
        request = FailureSummaryInput.model_validate(
            {"region": region, "window_hours": window_hours}
        )
        result: FailureSummary = await self._payments.failure_summary(request, self._context)
        return result.model_dump()

    def as_langchain_tools(self) -> list[StructuredTool]:
        return [
            StructuredTool.from_function(
                coroutine=self.get_failure_summary,
                name="payments_get_failure_summary",
                description=(
                    "Return aggregate payment failure statistics for an authorized region and "
                    "bounded time window. This tool is read-only and never exposes customer data."
                ),
                args_schema=FailureSummaryInput,
            )
        ]
