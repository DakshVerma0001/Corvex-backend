from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
from typing import List, Dict


class RawEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    timestamp: datetime
    raw_payload: Dict
    tenant_id: str = "default"


class NormalizedEvent(BaseModel):
    event_id: str
    tenant_id: str
    ecs: Dict
    source: str
    collected_at: datetime
    enrichments: Dict = {}


class ScoredDetection(BaseModel):
    event_id: str
    tenant_id: str
    composite_score: float
    severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    ttp_hints: List[str]
    attack_details: List[Dict]
    next_attack_predictions: List[Dict]
    model_scores: Dict
    shap_features: List[Dict] = []
    detected_at: datetime = Field(default_factory=datetime.utcnow)


class Incident(BaseModel):
    incident_id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    title: str
    severity: str
    status: str = "OPEN"
    autonomy_level: int
    detection: ScoredDetection
    affected_assets: List[str] = []
    actor: Dict = {}
    actions_taken: List[Dict] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)