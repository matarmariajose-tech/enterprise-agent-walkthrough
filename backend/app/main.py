from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Enterprise Agent Runtime",
    version="1.0.0",
    description="Sanitized reference implementation of a governed agent runtime.",
)
app.include_router(router)
