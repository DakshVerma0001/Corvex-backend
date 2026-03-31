import asyncio
import json
import os
from uuid import uuid4

import aio_pika
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")


async def send_message():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "detections",
        aio_pika.ExchangeType.TOPIC,
        durable=True
    )

    payload = {
        "id": str(uuid4()),
        "event_id": str(uuid4()),
        "entity_id": "192.168.1.50",
        "entity_type": "ip",
        "composite_score": 0.85,
        "individual_scores": {"modelA": 0.85},
        "contributing_models": ["modelA"],
        "shap_values": [
            {
                "feature_name": "failed_logins",
                "human_label": "Failed Logins",
                "shap_value": 0.4,
                "feature_value": 15
            }
        ],
        "sigma_matches": [],
        "ttp_hints": ["T1486"]
    }

    message = aio_pika.Message(
        body=json.dumps(payload).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )

    await exchange.publish(message, routing_key="detection.result")

    print("Detection message sent")

    await connection.close()


if __name__ == "__main__":
    asyncio.run(send_message())