from typing import List
from .models import SigmaMatch


CRITICAL_TTPS = {"T1486", "T1490", "T1561"}


def apply_overrides(
    base_severity: str,
    sigma_matches: List[SigmaMatch],
    ttp_hints: List[str]
) -> str:

    # 1. Sigma critical override
    if any(m.severity.lower() == "critical" for m in sigma_matches):
        return "CRITICAL"

    # 2. Ransomware / destructive techniques
    if any(ttp in CRITICAL_TTPS for ttp in ttp_hints):
        return "CRITICAL"

    # 3. Credential abuse combo
    if "T1078" in ttp_hints and "T1110" in ttp_hints:
        if base_severity in ["LOW", "MEDIUM"]:
            return "HIGH"

    return base_severity