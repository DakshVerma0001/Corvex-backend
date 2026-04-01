import aio_pika
from shared.models import ScoredDetection
from shared.events import (
    EXCHANGE_DETECTIONS,
    ROUTING_KEY_SCORED
)


async def publish_scored_detection(channel, detection: ScoredDetection):
    exchange = await channel.declare_exchange(
        EXCHANGE_DETECTIONS,
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    message = aio_pika.Message(
        body=detection.model_dump_json().encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        content_type="application/json"
    )

    await exchange.publish(
        message,
        routing_key=ROUTING_KEY_SCORED
    )