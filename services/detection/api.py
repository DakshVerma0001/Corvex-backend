from fastapi import APIRouter, HTTPException
from workers.detection_worker import DETECTIONS_STORE

router = APIRouter()


@router.get("/internal/detections")
async def list_detections(limit: int = 50):
    return list(DETECTIONS_STORE)[:limit]


@router.get("/internal/detections/{det_id}")
async def get_detection(det_id: str):
    for d in DETECTIONS_STORE:
        if d["id"] == det_id:
            return d
    raise HTTPException(404, "Detection not found")