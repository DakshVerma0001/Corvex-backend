import structlog

logger = structlog.get_logger()

# Minimal static index (replace with STIX later)
ATTACK_INDEX = {
    "T1110": {
        "name": "Brute Force",
        "tactic": "Credential Access",
        "description": "Adversaries may use brute force to guess passwords.",
        "sub_techniques": ["T1110.001", "T1110.003"],
        "mitigations": ["M1027", "M1032"],
        "data_sources": ["Authentication logs"],
    },
    "T1490": {
        "name": "Inhibit System Recovery",
        "tactic": "Impact",
        "description": "Delete backups/shadow copies to block recovery.",
        "sub_techniques": [],
        "mitigations": ["M1022"],
        "data_sources": ["Process creation"],
    },
}


def get_technique(technique_id: str):
    return ATTACK_INDEX.get(technique_id)