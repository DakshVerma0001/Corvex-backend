from sqlalchemy import Column, String, Float, JSON, Integer, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from .db import Base
import uuid


class IncidentRow(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_id = Column(UUID(as_uuid=True), unique=True, nullable=False)

    severity = Column(String, nullable=False)
    incident_type = Column(String, nullable=False)

    composite_score = Column(Float, nullable=False)

    shap_values = Column(JSON, nullable=False)
    individual_scores = Column(JSON, nullable=False)
    sigma_matches = Column(JSON)

    ttp_tags = Column(JSON, nullable=False)
    affected_assets = Column(JSON, nullable=False)

    autonomy_level = Column(Integer, nullable=False)
    kill_chain_prediction = Column(JSON)

    status = Column(String, default="open")
    feedback = Column(String, nullable=True)


class ActionAuditRow(Base):
    __tablename__ = "action_audit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)

    playbook_name = Column(String, nullable=False)
    action_name = Column(String, nullable=False)

    params = Column(JSON, nullable=False)
    result = Column(JSON)

    executed_at = Column(String, nullable=False)

    executed_by = Column(String, default="system")

    success = Column(Boolean)
    rolled_back = Column(Boolean, default=False)

    container_logs = Column(Text)