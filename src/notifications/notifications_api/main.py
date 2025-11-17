from contextlib import asynccontextmanager

from fastapi import FastAPI

from notifications.common.config import settings
from notifications.common.kafka import kafka_publisher
from notifications.notifications_api.api.v1.events import router as events_router
from notifications.notifications_api.api.v1.templates import router as templates_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await kafka_publisher.start()
    try:
        yield
    finally:
        # shutdown
        await kafka_publisher.stop()


app = FastAPI(
    title=settings.project_name,
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


app.include_router(events_router, prefix=settings.api_v1_prefix)
app.include_router(templates_router, prefix=settings.api_v1_prefix)