import asyncio
import structlog

logger = structlog.get_logger()


class EnrichmentPipeline:

    async def enrich(self, event):
        try:
            enrichments = {}

            # Example enrichment: check if IP exists
            if event.source_ip:
                enrichments["geo"] = await self._fake_geo_lookup(event.source_ip)
                enrichments["threat"] = await self._fake_threat_check(event.source_ip)

            event_dict = event.model_dump()
            event_dict["enrichments"] = enrichments

            return event_dict

        except Exception as e:
            logger.error("enrichment_failed", error=str(e))
            return event.model_dump()

    async def _fake_geo_lookup(self, ip):
        await asyncio.sleep(0.1)
        return {"country": "India", "city": "Delhi"}

    async def _fake_threat_check(self, ip):
        await asyncio.sleep(0.1)
        return {"malicious": False}