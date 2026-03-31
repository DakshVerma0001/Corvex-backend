from services.action.playbooks.loader import PlaybookLoader
from services.action.playbooks.matcher import find_matching_playbooks


class DummyIncident:
    def __init__(self):
        self.severity = "CRITICAL"
        self.ttp_tags = [{"technique_id": "T1486"}]


loader = PlaybookLoader()
playbooks = loader.load()

incident = DummyIncident()

matches = find_matching_playbooks(incident, playbooks)

for m in matches:
    print(m.name)