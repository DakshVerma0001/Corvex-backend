from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class NormalizedEvent(BaseModel):
    id: UUID
    timestamp: datetime
    ecs_version: str = "8.0"

    # event fields
    event_category: List[str]
    event_type: List[str]
    event_outcome: Optional[str] = None
    event_action: Optional[str] = None

    # user / host
    user_name: Optional[str] = None
    host_name: Optional[str] = None

    # source
    source_ip: Optional[str] = None

    # custom
    source_collector: str
    raw_payload: Dict[str, Any]

def map_to_ecs(raw_log):
    payload = raw_log.payload

    return NormalizedEvent(
        id=raw_log.id,
        timestamp=raw_log.collected_at,

        event_category=["authentication"] if payload.get("event") == "login" else ["unknown"],
        event_type=[payload.get("event", "unknown")],
        event_outcome=payload.get("status"),

        user_name=payload.get("user"),

        # 👇 IMPORTANT FIX
        source_ip=payload.get("source_ip"),

        source_collector=raw_log.source,
        raw_payload=payload
    )