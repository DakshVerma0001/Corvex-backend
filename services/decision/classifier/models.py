from pydantic import BaseModel
from typing import List, Dict, Any, Literal, Optional
from uuid import UUID


class SHAPFeature(BaseModel):
    feature_name: str
    human_label: str
    shap_value: float
    feature_value: float


class SigmaMatch(BaseModel):
    rule_id: str
    rule_name: str
    ttp_tags: List[str]
    severity: str
    matched_fields: Dict[str, str]


class DetectionResult(BaseModel):
    id: UUID
    event_id: UUID
    entity_id: str
    entity_type: Literal["user", "host", "ip", "process"]
    composite_score: float
    individual_scores: Dict[str, float]
    contributing_models: List[str]
    shap_values: List[SHAPFeature]
    sigma_matches: List[SigmaMatch]
    ttp_hints: List[str]


# -------- INCIDENT MODEL --------

class Incident(BaseModel):
    id: Optional[str] = None
    detection_id: UUID
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    incident_type: str
    composite_score: float
    shap_values: List[SHAPFeature]
    individual_scores: Dict[str, float]
    sigma_matches: List[SigmaMatch]
    ttp_tags: List[Dict[str, Any]]
    affected_assets: List[Dict[str, Any]]
    autonomy_level: int
    kill_chain_prediction: List[str]