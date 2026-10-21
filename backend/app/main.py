from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.domain.errors import (
    AuthorizationError,
    IdempotencyConflictError,
    InsufficientEvidenceError,
    PolicyUnavailableError,
)

app = FastAPI(
    title="Enterprise Agent Runtime",
    version="1.0.0",
    description="Sanitized reference implementation of a governed agent runtime.",
)
app.include_router(router)

ERROR_RESPONSES: dict[type[Exception], tuple[int, str, str]] = {
    AuthorizationError: (403, "forbidden", "The operation is outside the authorized scope"),
    IdempotencyConflictError: (
        409,
        "idempotency_conflict",
        "Correlation ID was already used for a different request",
    ),
    InsufficientEvidenceError: (422, "insufficient_evidence", "No suitable evidence was found"),
    PolicyUnavailableError: (503, "policy_unavailable", "The policy could not be evaluated"),
}


@app.middleware("http")
async def correlate_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request.state.trace_id = uuid4().hex
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.trace_id
    return response


async def handle_domain_error(request: Request, error: Exception) -> JSONResponse:
    status, code, message = ERROR_RESPONSES[type(error)]
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "trace_id": request.state.trace_id}},
    )


for error_type in ERROR_RESPONSES:
    app.add_exception_handler(error_type, handle_domain_error)
