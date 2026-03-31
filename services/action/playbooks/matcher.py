from typing import Dict, List
from services.action.playbooks.loader import Playbook


def find_matching_playbooks(
    incident,
    all_playbooks: Dict[str, Playbook]
) -> List[Playbook]:

    matches = []

    for pb in all_playbooks.values():

        # Severity match
        severity_match = (
            pb.triggers.severity is None or
            incident.severity in pb.triggers.severity
        )

        # Extract TTPs from incident
        incident_ttps = [t["technique_id"] for t in incident.ttp_tags]

        # TTP match
        ttp_match = (
            pb.triggers.ttp is None or
            bool(set(pb.triggers.ttp) & set(incident_ttps))
        )

        if severity_match and ttp_match:
            matches.append(pb)

    # Sort by risk level (CRITICAL first)
    priority = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1
    }

    return sorted(matches, key=lambda p: priority.get(p.risk_level, 0), reverse=True)