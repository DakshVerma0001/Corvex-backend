from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, func, update
from uuid import UUID
from pydantic import BaseModel

from services.decision.db import AsyncSessionLocal
from services.decision.models import IncidentRow, ActionAuditRow

router = APIRouter()


class UpdateStatusRequest(BaseModel):
    status: str


class FeedbackRequest(BaseModel):
    feedback: str


@router.get("/")
async def get_incidents(
    severity: str | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    async with AsyncSessionLocal() as session:

        query = select(IncidentRow)

        if severity:
            query = query.where(IncidentRow.severity == severity)

        if status:
            query = query.where(IncidentRow.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await session.execute(query)
        incidents = result.scalars().all()

        return {
            "items": [
                {
                    "id": str(i.id),
                    "severity": i.severity,
                    "incident_type": i.incident_type,
                    "status": i.status,
                    "autonomy_level": i.autonomy_level
                }
                for i in incidents
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": offset + page_size < total
        }


@router.get("/{incident_id}")
async def get_incident_by_id(incident_id: UUID):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(IncidentRow).where(IncidentRow.id == incident_id)
        )
        incident = result.scalar_one_or_none()

        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")

        return {
            "id": str(incident.id),
            "detection_id": str(incident.detection_id),
            "severity": incident.severity,
            "incident_type": incident.incident_type,
            "status": incident.status,
            "feedback": incident.feedback,
            "composite_score": incident.composite_score,
            "shap_values": incident.shap_values,
            "individual_scores": incident.individual_scores,
            "sigma_matches": incident.sigma_matches,
            "ttp_tags": incident.ttp_tags,
            "affected_assets": incident.affected_assets,
            "autonomy_level": incident.autonomy_level,
            "kill_chain_prediction": incident.kill_chain_prediction
        }


@router.patch("/{incident_id}/status")
async def update_incident_status(
    incident_id: UUID,
    request: UpdateStatusRequest
):
    allowed_status = {"investigating", "contained", "closed", "false_positive"}

    if request.status not in allowed_status:
        raise HTTPException(status_code=400, detail="Invalid status value")

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(IncidentRow).where(IncidentRow.id == incident_id)
        )
        incident = result.scalar_one_or_none()

        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")

        await session.execute(
            update(IncidentRow)
            .where(IncidentRow.id == incident_id)
            .values(status=request.status)
        )

        await session.commit()

        return {
            "message": "Status updated successfully",
            "incident_id": str(incident_id),
            "new_status": request.status
        }


@router.post("/{incident_id}/feedback")
async def submit_feedback(
    incident_id: UUID,
    request: FeedbackRequest
):
    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(IncidentRow).where(IncidentRow.id == incident_id)
        )
        incident = result.scalar_one_or_none()

        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")

        await session.execute(
            update(IncidentRow)
            .where(IncidentRow.id == incident_id)
            .values(feedback=request.feedback)
        )

        await session.commit()

        return {
            "message": "Feedback submitted successfully",
            "incident_id": str(incident_id),
            "feedback": request.feedback
        }


# 🚀 NEW TIMELINE ENDPOINT
@router.get("/{incident_id}/timeline")
async def get_incident_timeline(incident_id: UUID):
    async with AsyncSessionLocal() as session:

        # Get incident
        result = await session.execute(
            select(IncidentRow).where(IncidentRow.id == incident_id)
        )
        incident = result.scalar_one_or_none()

        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")

        # Get actions
        actions_result = await session.execute(
            select(ActionAuditRow)
            .where(ActionAuditRow.incident_id == incident_id)
        )
        actions = actions_result.scalars().all()

        timeline = []

        # Detection event
        timeline.append({
            "type": "detection",
            "timestamp": "N/A",
            "details": {
                "severity": incident.severity,
                "incident_type": incident.incident_type,
                "composite_score": incident.composite_score
            }
        })

        # Action events
        for action in actions:
            timeline.append({
                "type": "action",
                "timestamp": action.executed_at,
                "details": {
                    "action_name": action.action_name,
                    "success": action.success,
                    "params": action.params
                }
            })

        return timeline