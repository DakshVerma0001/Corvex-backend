from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Histogram, generate_latest
import time
import asyncio

from services.knowledge.attack.loader import get_technique
from services.knowledge.attack.predictor import predict_next
from services.knowledge.learning.feedback_consumer import FeedbackConsumer

app = FastAPI(title="Knowledge Service", docs_url="/internal/docs")
from services.ingestion.pipeline.worker import IngestionWorker
import asyncio

worker = IngestionWorker()
consumer = FeedbackConsumer()

# metrics
REQUEST_COUNT = Counter(
    "knowledge_requests_total",
    "Total requests to knowledge service",
    ["endpoint"]
)

REQUEST_LATENCY = Histogram(
    "knowledge_request_latency_seconds",
    "Latency of requests"
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = time.time() - start

    REQUEST_COUNT.labels(endpoint=request.url.path).inc()
    REQUEST_LATENCY.observe(latency)

    return response


@app.on_event("startup")
async def startup():
    asyncio.create_task(worker.start())


@app.get("/internal/health")
async def health():
    return {"status": "ok"}


@app.get("/internal/metrics")
async def metrics():
    return PlainTextResponse(generate_latest(), media_type="text/plain")


@app.get("/internal/attack/technique/{technique_id}")
async def technique(technique_id: str):
    data = get_technique(technique_id)
    if not data:
        raise HTTPException(404, "Technique not found")
    return {"technique_id": technique_id, **data}


@app.get("/internal/attack/predict-next")
async def predict(ttps: str, k: int = 3):
    tlist = [t.strip() for t in ttps.split(",") if t.strip()]
    return predict_next(tlist, k=k)