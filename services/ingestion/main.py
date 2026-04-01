import asyncio
import structlog
from fastapi import FastAPI
from contextlib import asynccontextmanager
from services.ingestion.pipeline.worker import IngestionWorker

# 👇 YE IMPORT ADD KARNA HAI
from services.ingestion.collectors.webhook import router as webhook_router

logger = structlog.get_logger()
worker = IngestionWorker()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_ingestion_service")

    worker_task = asyncio.create_task(worker.start())

    yield

    logger.info("stopping_ingestion_service")
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

# 👇 YAHAN PE ADD KARNA HAI
app = FastAPI(lifespan=lifespan)

# 👇 ISKE JUST NEECHAY
app.include_router(webhook_router, prefix="/ingest")

@app.get("/health")
async def health():
    return {"status": "ok"}