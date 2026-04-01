import asyncio
from fastapi import FastAPI
from workers.detection_worker import DetectionWorker
from api import router as detections_router

app = FastAPI(title="Detection Service", docs_url="/internal/docs")
app.include_router(detections_router)


@app.on_event("startup")
async def startup():
    worker = DetectionWorker()
    asyncio.create_task(worker.start())