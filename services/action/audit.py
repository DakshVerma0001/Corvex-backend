from datetime import datetime
from services.decision.db import AsyncSessionLocal
from services.decision.models import ActionAuditRow


async def log_action_audit(
    incident_id,
    playbook_name,
    action_name,
    params,
    result,
    success,
    logs
):
    async with AsyncSessionLocal() as session:
        row = ActionAuditRow(
            incident_id=incident_id,
            playbook_name=playbook_name,
            action_name=action_name,
            params=params,
            result=result,
            executed_at=datetime.utcnow().isoformat(),
            success=success,
            container_logs=logs
        )

        session.add(row)
        await session.commit()