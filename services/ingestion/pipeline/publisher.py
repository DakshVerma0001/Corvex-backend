import aio_pika
import asyncio
import structlog

logger = structlog.get_logger()


class EventPublisher:

    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            "amqp://guest:guest@localhost/"
        )
        self.channel = await self.connection.channel()

    async def publish(self, message: str):
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key="events.normalized"
        )

        # 👇 YE LINE IMPORTANT HAI
        logger.info("event_published")