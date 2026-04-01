import aio_pika
import asyncio
import os

from shared.models import ScoredDetection
from shared.events import (
    EXCHANGE_DETECTIONS,
    QUEUE_DETECTIONS_SCORED,
    ROUTING_KEY_SCORED
)


from services.decision.classifier import incident_classifier as classify_detection
from services.action.playbooks import executor as execute_playbook
from services.action.audit import log_action_audit as log_audit_entry
from services.decision.db import save_incident_to_db  # adjust if different

# fallback logger
try:
    import structlog
    logger = structlog.get_logger()
except:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


def assign_autonomy(score: float) -> int:
    if score < 0.3:
        return 1
    elif score < 0.6:
        return 2
    elif score < 0.85:
        return 3
    return 4


async def process_detection(detection: ScoredDetection):
    # 1. classify
    incident = await classify_detection(detection)

    # 2. autonomy
    incident.autonomy_level = assign_autonomy(detection.composite_score)

    # 3. automated response
    if incident.autonomy_level >= 3:
        await execute_playbook(incident)

    # 4. save
    await save_incident_to_db(incident)

    # 5. audit
    await log_audit_entry(incident)

    logger.info("incident_created", severity=incident.severity)


async def start_consumer():
    connection = await aio_pika.connect_robust(
        os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
    )

    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)

    exchange = await channel.declare_exchange(
        EXCHANGE_DETECTIONS,
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    queue = await channel.declare_queue(
        QUEUE_DETECTIONS_SCORED,
        durable=True
    )

    await queue.bind(exchange, routing_key=ROUTING_KEY_SCORED)

    async def on_message(message: aio_pika.IncomingMessage):
        async with message.process():
            try:
                detection = ScoredDetection.model_validate_json(
                    message.body
                )
                await process_detection(detection)
            except Exception as e:
                logger.error("consumer_error", error=str(e))
                await message.nack(requeue=False)

    await queue.consume(on_message)

    logger.info("incident_consumer_started")

    while True:
        await asyncio.sleep(5)