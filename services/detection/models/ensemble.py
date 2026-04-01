from datetime import datetime
from uuid import uuid4
import structlog

logger = structlog.get_logger()


class EnsembleScorer:

    async def score(
        self,
        event,
        stat_score,
        if_score,
        lstm_score,
        sigma_matches,
        shap_values
    ):

        weights = {
            "statistical": 0.25,
            "isolation_forest": 0.30,
            "lstm": 0.30,
            "sigma": 0.15
        }

        sigma_score = min(len(sigma_matches) * 0.15, weights["sigma"])

        composite = (
            weights["statistical"] * stat_score +
            weights["isolation_forest"] * if_score +
            weights["lstm"] * (lstm_score or 0.0) +
            weights["sigma"] * sigma_score
        )

        composite = max(0.0, min(1.0, composite))

        # ✅ entity logic
        entity_id = f"user:{event.get('user_name') or 'unknown'}"

        entity_type = "user"
        if event.get("source_ip"):
            entity_type = "ip"
        elif event.get("host_name"):
            entity_type = "host"

        # ✅ ensure 5 shap values
        shap_values = shap_values[:5]
        while len(shap_values) < 5:
            shap_values.append(shap_values[0])

        result = {
            "id": str(uuid4()),
            "event_id": str(event.get("id")),
            "entity_id": entity_id,
            "entity_type": entity_type,
            "composite_score": float(composite),

            "individual_scores": {
                "statistical": float(stat_score),
                "isolation_forest": float(if_score),
                "lstm": float(lstm_score or 0.0),
                "sigma": float(sigma_score),
            },

            "contributing_models": [
                k for k, v in {
                    "statistical": stat_score,
                    "isolation_forest": if_score,
                    "lstm": lstm_score,
                    "sigma": sigma_score
                }.items() if v is not None
            ],

            "shap_values": shap_values,

            "sigma_matches": sigma_matches,
            "ttp_hints": [t for m in sigma_matches for t in m["ttp_tags"]],

            "raw_event_ref": str(event.get("id")),
            "normalized_event": event,   # ✅ already dict

            "detected_at": datetime.utcnow().isoformat(),
            "detection_latency_ms": 0.0
        }

        logger.info("ensemble_result_created")

        return result