from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.agent.orchestrator import AgentOrchestrator
from app.api.dependencies import execution_context, orchestrator
from app.domain.models import AgentRequest, AgentResponse, ExecutionContext

router = APIRouter(prefix="/v1")


@router.get("/health", status_code=status.HTTP_200_OK)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/agent/requests", response_model=AgentResponse)
async def execute_request(
    request: AgentRequest,
    context: Annotated[ExecutionContext, Depends(execution_context)],
    agent: Annotated[AgentOrchestrator, Depends(orchestrator)],
) -> AgentResponse:
    result: AgentResponse = await agent.chain.ainvoke((request, context))
    return result
