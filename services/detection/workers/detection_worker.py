import asyncio
import json
import time
import os
from collections import deque

import aio_pika

# ✅ Shared contracts
from shared.models import ScoredDetection
from shared.events import (
    EXCHANGE_EVENTS,
    QUEUE_EVENTS_NORMALIZED,
    ROUTING_KEY_NORMALIZED,
)

# ✅ Internal modules
from services.detection.publisher import publish_scored_detection
from services.detection.models.sigma_engine import SigmaEngine
from services.detection.models.ensemble import EnsembleScorer

# -------- Logging (safe fallback) --------
try:
    import structlog
    logger = structlog.get_logger()
except:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# -------- Optional Redis (non-blocking) --------
try:
    import redis.asyncio as aioredis
    redis_client = aioredis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        decode_responses=True
    )
except:
    redis_client = None

# -------- Engines --------
sigma_engine = SigmaEngine()
ensemble = EnsembleScorer()

DETECTIONS_STORE = deque(maxlen=500)


# -------- Helper Functions --------

def compute_sigma_score(sigma_matches):
    return min(len(sigma_matches) * 0.3, 1.0)


def compute_score(event):
    return 1.0 if event.get("event_outcome") == "failure" else 0.1


# -------- Worker --------

class DetectionWorker:

    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self):
        print("🔌 Connecting to RabbitMQ...")

        self.connection = await aio_pika.connect_robust(
            os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
        )

        self.channel = await self.connection.channel()

        exchange = await self.channel.declare_exchange(
            EXCHANGE_EVENTS,
            aio_pika.ExchangeType.DIRECT,
            durable=True
        )

        self.queue = await self.channel.declare_queue(
            QUEUE_EVENTS_NORMALIZED,
            durable=True
        )

        await self.queue.bind(exchange, routing_key=ROUTING_KEY_NORMALIZED)

        print("✅ Connected to RabbitMQ and queue bound")
        logger.info("detection_worker_connected")

    async def start(self):
        await self.connect()

        print("🚀 DetectionWorker started and waiting for messages...")

        await self.queue.consume(self.handle_message)

        logger.info("detection_worker_started")

        while True:
            await asyncio.sleep(5)

    async def handle_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                event = json.loads(message.body.decode())
                print("📩 Received event:", event)

                sigma_matches = sigma_engine.evaluate(event)

                stat_score = compute_score(event)
                sigma_score = compute_sigma_score(sigma_matches)

                result = await ensemble.score(
                    event,
                    stat_score,
                    0.0,
                    None,
                    sigma_matches,
                    []
                )

                # -------- Convert to ScoredDetection --------
                detection = ScoredDetection(
                    event_id=event.get("event_id", "unknown"),
                    tenant_id=event.get("tenant_id", "default"),
                    composite_score=result.get("composite_score", 0.5),
                    severity=result.get("severity", "MEDIUM"),
                    ttp_hints=result.get("ttp_hints", []),
                    attack_details=[],
                    next_attack_predictions=[],
                    model_scores={
                        "stat": stat_score,
                        "sigma": sigma_score
                    },
                    shap_features=[]
                )

                DETECTIONS_STORE.appendleft(detection.model_dump())

                print("⚡ Detection created:", detection.composite_score)

                logger.info(
                    "detection_created",
                    score=detection.composite_score
                )

                # ✅ Publish to incident pipeline
                await publish_scored_detection(self.channel, detection)

                print("📤 Published to detections.scored")

                logger.info("detection_published_to_incident_pipeline")

            except Exception as e:
                print("❌ Error in detection:", str(e))
                logger.error("detection_error", error=str(e))


# -------- ENTRY POINT (CRITICAL FIX) --------

if __name__ == "__main__":
    print("🔥 Starting Detection Worker...")

    worker = DetectionWorker()
    asyncio.run(worker.start())