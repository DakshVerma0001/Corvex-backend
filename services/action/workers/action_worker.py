import asyncio
import json
import os
import subprocess

import aio_pika
from dotenv import load_dotenv

from services.action.audit import log_action_audit
from services.action.playbooks.loader import PlaybookLoader
from services.action.playbooks.matcher import find_matching_playbooks
from services.action.playbooks.executor import PlaybookExecutor

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")


class Incident:
    def __init__(self, payload: dict):
        self.id = payload.get("incident_id")
        self.entity_id = payload.get("entity_id")
        self.severity = payload.get("severity")
        self.ttp_tags = payload.get("ttp_tags", [])


class ActionWorker:

    def __init__(self):
        # ✅ Playbook system init
        self.loader = PlaybookLoader()
        self.playbooks = self.loader.load()
        self.executor = PlaybookExecutor()

    async def start(self):
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        exchange = await channel.declare_exchange(
            "actions",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        queue = await channel.declare_queue(
            "action_queue",
            durable=True
        )

        await queue.bind(exchange, routing_key="action.execute")

        print("Action Worker (Hybrid Mode) started...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await self.handle_message(message)

    async def handle_message(self, message: aio_pika.IncomingMessage):
        try:
            payload = json.loads(message.body.decode())

            print(f"Received Action: {payload}")

            incident = Incident(payload)

            # ✅ Try playbook execution first
            handled = await self.process_with_playbooks(incident)

            # ✅ Fallback to old logic if no playbook matched
            if not handled:
                await self.execute_action(payload)

        except Exception as e:
            print(f"Action error: {e}")

    async def process_with_playbooks(self, incident: Incident) -> bool:
        matches = find_matching_playbooks(incident, self.playbooks)

        if not matches:
            print("No matching playbooks found, using fallback logic")
            return False

        for playbook in matches:
            print(f"Executing playbook: {playbook.name}")

            result = await self.executor.execute(playbook, incident)

            print(f"Playbook result: {result.success}")

        return True

    async def execute_action(self, payload: dict):
        action_type = payload.get("action_type")
        entity_id = payload.get("entity_id")
        incident_id = payload.get("incident_id")

        params = {"entity_id": entity_id}

        try:
            if action_type == "full_containment":
                ip = entity_id

                cmd = [
                    "python",
                    "services/action/runners/linux_runner/runner.py",
                    "--action",
                    "linux.firewall.block_ip",
                    "--params-json",
                    json.dumps({"ip": ip})
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)

                output = result.stdout
                success = result.returncode == 0
                logs = result.stdout + result.stderr

                print(f"Action Result: {output}")

            elif action_type == "isolate":
                output = f"Isolating entity: {entity_id}"
                success = True
                logs = output

                print(output)

            elif action_type == "collect_evidence":
                output = f"Collecting evidence for: {entity_id}"
                success = True
                logs = output

                print(output)

            else:
                output = "Unknown action"
                success = False
                logs = output

                print(output)

            # ✅ AUDIT LOGGING
            await log_action_audit(
                incident_id=incident_id,
                playbook_name="default",
                action_name=action_type,
                params=params,
                result={"output": output},
                success=success,
                logs=logs
            )

        except Exception as e:
            await log_action_audit(
                incident_id=incident_id,
                playbook_name="default",
                action_name=action_type,
                params=params,
                result={},
                success=False,
                logs=str(e)
            )

            print(f"Execution failed: {e}")


if __name__ == "__main__":
    worker = ActionWorker()
    asyncio.run(worker.start())