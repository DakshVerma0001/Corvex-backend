from pydantic import BaseModel, Field
from typing import Any, Dict
from uuid import UUID, uuid4
from datetime import datetime


class RawLog(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source: str
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any]