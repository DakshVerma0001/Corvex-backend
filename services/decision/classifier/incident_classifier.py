from typing import List
from .models import DetectionResult, Incident
from . import severity_rules

from services.decision.db import AsyncSessionLocal
from services.decision.models import IncidentRow
from services.decision.autonomy.autonomy_engine import AutonomyEngine
from services.decision.ttp_resolver import TTPResolver
from services.decision.kill_chain import KillChainPredictor


class IncidentClassifier:

    def __init__(self):
        self.autonomy_engine = AutonomyEngine()
        self.ttp_resolver = TTPResolver()
        self.kill_chain_predictor = KillChainPredictor()

    def _score_to_severity(self, score: float) -> str:
        if score >= 0.80:
            return "CRITICAL"
        elif score >= 0.65:
            return "HIGH"
        elif score >= 0.40:
            return "MEDIUM"
        return "LOW"

    def _derive_incident_type(self, ttp_hints: List[str]) -> str:
        if not ttp_hints:
            return "unknown"

        if "T1486" in ttp_hints:
            return "ransomware"
        if "T1110" in ttp_hints:
            return "brute_force"
        if "T1078" in ttp_hints:
            return "credential_abuse"

        return "suspicious_activity"

    def _extract_assets(self, entity_id: str, entity_type: str):
        return [{
            "type": entity_type,
            "id": entity_id
        }]

    def _compute_autonomy(self, score: float, severity: str) -> int:
        if severity == "CRITICAL" or score >= 0.80:
            return 4
        if severity == "HIGH" or score >= 0.65:
            return 3
        if severity == "MEDIUM" or score >= 0.40:
            return 2
        return 1

    async def classify(self, result: DetectionResult) -> Incident:

        # 1. Base severity
        severity = self._score_to_severity(result.composite_score)

        # 2. Apply overrides
        severity = severity_rules.apply_overrides(
            severity,
            result.sigma_matches,
            result.ttp_hints
        )

        # 3. Incident type
        incident_type = self._derive_incident_type(result.ttp_hints)

        # 4. Assets
        assets = self._extract_assets(
            result.entity_id,
            result.entity_type
        )

        # 5. Autonomy
        autonomy_level = self._compute_autonomy(
            result.composite_score,
            severity
        )

        # 6. TTP enrichment
        enriched_ttps = await self.ttp_resolver.enrich(result.ttp_hints)

        # 7. Kill chain prediction
        kill_chain = self.kill_chain_predictor.predict(enriched_ttps)

        # 8. Create Incident
        incident = Incident(
            detection_id=result.id,
            severity=severity,
            incident_type=incident_type,
            composite_score=result.composite_score,
            shap_values=result.shap_values,
            individual_scores=result.individual_scores,
            sigma_matches=result.sigma_matches,
            ttp_tags=enriched_ttps,
            affected_assets=assets,
            autonomy_level=autonomy_level,
            kill_chain_prediction=kill_chain,
        )

        # 9. Save to DB (FIXED)
        async with AsyncSessionLocal() as session:
            try:
                db_row = IncidentRow(
                    detection_id=incident.detection_id,
                    severity=incident.severity,
                    incident_type=incident.incident_type,
                    composite_score=incident.composite_score,
                    shap_values=[s.model_dump() for s in incident.shap_values],
                    individual_scores=incident.individual_scores,
                    sigma_matches=[m.model_dump() for m in incident.sigma_matches],
                    ttp_tags=incident.ttp_tags,
                    affected_assets=incident.affected_assets,
                    autonomy_level=incident.autonomy_level,
                    kill_chain_prediction=incident.kill_chain_prediction,
                )

                print("Saving incident to DB...")

                session.add(db_row)
                await session.commit()
                await session.refresh(db_row)

                print("DB commit successful")

                # IMPORTANT: assign ID back
                incident.id = str(db_row.id)

            except Exception as e:
                print("DB ERROR:", e)
                raise

        print(f"Autonomy Level: {incident.autonomy_level}")

        # 10. Dispatch action
        await self.autonomy_engine.dispatch(incident)

        return incident