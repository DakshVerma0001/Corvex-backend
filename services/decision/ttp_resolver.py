import os
import httpx

KNOWLEDGE_API_URL = os.getenv("KNOWLEDGE_API_URL", "http://localhost:9000")


class TTPResolver:

    async def enrich(self, ttp_ids):
        """
        Input: ["T1486", "T1110"]
        Output: enriched data
        """

        enriched = []

        for ttp in ttp_ids:
            data = await self._fetch_ttp(ttp)
            enriched.append(data)

        return enriched

    async def _fetch_ttp(self, ttp_id: str):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{KNOWLEDGE_API_URL}/ttp/{ttp_id}"
                )

                if response.status_code == 200:
                    return response.json()

        except Exception:
            pass

        # ✅ Fallback (VERY IMPORTANT)
        return {
            "technique_id": ttp_id,
            "name": "Unknown",
            "tactic": "unknown",
            "risk": "medium"
        }