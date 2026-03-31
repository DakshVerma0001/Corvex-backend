from typing import List


class KillChainPredictor:

    def predict(self, ttp_tags: List[dict]) -> List[str]:
        """
        Input: enriched TTPs
        Output: next likely techniques
        """

        techniques = [t.get("technique_id") for t in ttp_tags]

        predictions = []

        # Simple mapping (can be upgraded later)
        if "T1486" in techniques:
            predictions.extend(["T1490", "T1027"])  # ransomware follow-ups

        if "T1110" in techniques:
            predictions.extend(["T1078", "T1059"])  # brute force → access

        if "T1078" in techniques:
            predictions.extend(["T1041", "T1105"])  # credential abuse → exfil

        return list(set(predictions))