from services.decision.db import AsyncSessionLocal
from services.decision.models import IncidentRow, ActionAuditRow
from sqlalchemy import select


class ContextBuilder:

    async def build(self, incident_id):
        async with AsyncSessionLocal() as session:

            # Fetch incident
            result = await session.execute(
                select(IncidentRow).where(IncidentRow.id == incident_id)
            )
            incident = result.scalar_one_or_none()

            if not incident:
                return None

            # Fetch actions
            actions_result = await session.execute(
                select(ActionAuditRow)
                .where(ActionAuditRow.incident_id == incident_id)
            )
            actions = actions_result.scalars().all()

            # Build structured context
            context = {
                "incident": {
                    "severity": incident.severity,
                    "type": incident.incident_type,
                    "score": incident.composite_score,
                    "status": incident.status,
                    "autonomy_level": incident.autonomy_level,
                },
                "ttps": incident.ttp_tags,
                "kill_chain": incident.kill_chain_prediction,
                "actions": [
                    {
                        "action": a.action_name,
                        "success": a.success,
                        "timestamp": a.executed_at
                    }
                    for a in actions
                ]
            }

            return context