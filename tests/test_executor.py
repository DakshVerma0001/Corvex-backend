import asyncio

from services.action.playbooks.loader import PlaybookLoader
from services.action.playbooks.matcher import find_matching_playbooks
from services.action.playbooks.executor import PlaybookExecutor
import uuid

class MockIncident:
    def __init__(self):
        self.id = uuid.uuid4()
        self.entity_id = "192.168.1.100"
        self.severity = "CRITICAL"
        self.ttp_tags = [{"technique_id": "T1486"}]


async def main():
    loader = PlaybookLoader()
    playbooks = loader.load()

    incident = MockIncident()

    matches = find_matching_playbooks(incident, playbooks)

    executor = PlaybookExecutor()

    for pb in matches:
        result = await executor.execute(pb, incident)
        print("Execution Result:", result.success)


asyncio.run(main())