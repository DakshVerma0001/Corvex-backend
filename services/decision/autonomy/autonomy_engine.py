import os
import json

import aio_pika
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")

L2_THRESHOLD = float(os.getenv("AUTONOMY_L2_THRESHOLD", 0.40))
L3_THRESHOLD = float(os.getenv("AUTONOMY_L3_THRESHOLD", 0.65))
L4_THRESHOLD = float(os.getenv("AUTONOMY_L4_THRESHOLD", 0.80))


class AutonomyEngine:

    def compute_level(self, score: float, severity: str) -> int:
        if severity == "CRITICAL" or score >= L4_THRESHOLD:
            return 4
        if severity == "HIGH" or score >= L3_THRESHOLD:
            return 3
        if severity == "MEDIUM" or score >= L2_THRESHOLD:
            return 2
        return 1

    async def dispatch(self, incident):
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            "actions",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        level = incident.autonomy_level

        # 🔥 SAFE ENTITY EXTRACTION
        entity_id = None

        if incident.affected_assets:
            try:
                entity_id = incident.affected_assets[0].get("id")
            except Exception:
                entity_id = None

        print(f"🔍 Extracted entity_id: {entity_id}")  # debug

        action_request = {
            "incident_id": str(incident.detection_id),
            "severity": incident.severity,
            "action_type": None,
            "entity_id": entity_id
        }

        if level == 1:
            print("Level 1: Notify only")

        elif level == 2:
            action_request["action_type"] = "collect_evidence"

        elif level == 3:
            action_request["action_type"] = "isolate"

        elif level == 4:
            action_request["action_type"] = "full_containment"

        if action_request["action_type"]:
            message = aio_pika.Message(
                body=json.dumps(action_request).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await exchange.publish(message, routing_key="action.execute")

            print(f" Action dispatched: {action_request}")

        await connection.close()