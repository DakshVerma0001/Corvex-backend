import asyncio
import json
import structlog
import aio_pika
print("WORKER FILE LOADED")
from services.ingestion.normalizers.ecs import map_to_ecs
from services.ingestion.normalizers.enricher import EnrichmentPipeline
from services.ingestion.collectors.base import RawLog
logger = structlog.get_logger()
enricher = EnrichmentPipeline()


class IngestionWorker:

    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            "amqp://guest:guest@localhost/"
        )
        self.channel = await self.connection.channel()

       

        # queue
        self.queue = await self.channel.declare_queue(
            "events.raw",
            durable=True
        )

     

        logger.info("ingestion_worker_connected")

    async def start(self):
        if self.connection is None:
            await self.connect()

        await self.queue.consume(self.handle_message)

        logger.info("ingestion_worker_started")

        while True:
            await asyncio.sleep(5)

    async def handle_message(self, message: aio_pika.IncomingMessage):
        async with message.process():

            payload = json.loads(message.body.decode())

            logger.info("raw_event_received", payload=payload)

            # normalize
            raw_log = RawLog(
                source="webhook",
                payload=payload
            )

            normalized = map_to_ecs(raw_log)

            # enrich
            enriched = await enricher.enrich(normalized)

            logger.info("event_processed")

            # publish to detection
            exchange = await self.channel.declare_exchange(
                "events.normalized",
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

            exchange = await self.channel.declare_exchange(
                "events.normalized",
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )

            await exchange.publish(
               aio_pika.Message(
                  body=json.dumps(enriched, default=str).encode()
                ),
                routing_key="events.normalized"
            )

            logger.info("event_sent_to_detection")