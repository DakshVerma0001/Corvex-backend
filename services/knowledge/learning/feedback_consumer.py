import asyncio
import json
from datetime import datetime, timedelta
from collections import deque, defaultdict

import aio_pika
import structlog
import redis.asyncio as aioredis

logger = structlog.get_logger()

FEEDBACK_EVENTS = deque(maxlen=5000)

redis = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)

DEFAULT_WEIGHTS = {
    "statistical": 0.25,
    "isolation_forest": 0.30,
    "lstm": 0.30,
    "sigma": 0.15
}


class FeedbackConsumer:

    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        self.channel = await self.connection.channel()

        exchange = await self.channel.declare_exchange(
            "analyst.feedback",
            aio_pika.ExchangeType.FANOUT,
            durable=True
        )

        self.queue = await self.channel.declare_queue("", exclusive=True)
        await self.queue.bind(exchange)

        logger.info("feedback_consumer_connected")

    async def start(self):
        if self.connection is None:
            await self.connect()

        await self.queue.consume(self.handle_message)
        logger.info("feedback_consumer_started")

        while True:
            await asyncio.sleep(10)
            await self.adjust_weights()

    async def handle_message(self, message: aio_pika.IncomingMessage):
        async with message.process():
            data = json.loads(message.body.decode())

            data["received_at"] = datetime.utcnow().isoformat()
            FEEDBACK_EVENTS.append(data)

            logger.info("feedback_received", verdict=data.get("verdict"))

    async def adjust_weights(self):
        now = datetime.utcnow()
        cutoff = now - timedelta(days=7)

        counts = defaultdict(lambda: {"fp": 0, "total": 0})

        for f in FEEDBACK_EVENTS:
            t = datetime.fromisoformat(f["submitted_at"])
            if t < cutoff:
                continue

            scores = f.get("model_scores", {})
            verdict = f.get("verdict")

            for model in scores.keys():
                counts[model]["total"] += 1
                if verdict == "false_positive":
                    counts[model]["fp"] += 1

        current = await redis.get("ensemble:weights")
        if current:
            weights = json.loads(current)
        else:
            weights = DEFAULT_WEIGHTS.copy()

        for m, c in counts.items():
            if c["total"] == 0:
                continue
            fp_rate = c["fp"] / c["total"]

            if fp_rate > 0.05:
                weights[m] = weights.get(m, 0.25) * (1 - fp_rate)

        total = sum(weights.values()) or 1.0
        weights = {k: v / total for k, v in weights.items()}

        await redis.set("ensemble:weights", json.dumps(weights))

        logger.info("weights_updated", weights=weights)