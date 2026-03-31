import asyncio
import json
import os

import aio_pika
from dotenv import load_dotenv

from services.decision.classifier.incident_classifier import IncidentClassifier
from services.decision.classifier.models import DetectionResult

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")


class DecisionWorker:

    def __init__(self):
        self.classifier = IncidentClassifier()

    async def start(self):
        connection = await aio_pika.connect_robust(RABBITMQ_URL)

        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        # Declare exchange
        exchange = await channel.declare_exchange(
            "detections",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        # Declare queue
        queue = await channel.declare_queue(
            "decision_queue",
            durable=True
        )

        # Bind queue to routing key
        await queue.bind(exchange, routing_key="detection.result")

        print("🚀 Decision Worker started. Waiting for messages...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await self.handle_message(message)

    async def handle_message(self, message: aio_pika.IncomingMessage):
        try:
            payload = json.loads(message.body.decode())

            detection = DetectionResult(**payload)

            incident = await self.classifier.classify(detection)

            print(f"✅ Processed Incident: {incident.detection_id} | {incident.severity}")

        except Exception as e:
            print(f"❌ Error processing message: {e}")


if __name__ == "__main__":
    worker = DecisionWorker()
    asyncio.run(worker.start())