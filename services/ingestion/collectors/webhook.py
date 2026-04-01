import json
import aio_pika
import structlog
from fastapi import APIRouter, Request

logger = structlog.get_logger()
router = APIRouter()


@router.post("/webhook")
async def ingest_webhook(request: Request):

    payload = await request.json()

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "events.raw",
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    await channel.default_exchange.publish(
        aio_pika.Message(body=json.dumps(payload).encode()),
        routing_key="events.raw"
    )

    logger.info("raw_event_published")

    return {"status": "queued"}