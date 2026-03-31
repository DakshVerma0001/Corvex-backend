import asyncio
from uuid import uuid4
from services.decision.classifier.models import DetectionResult, SHAPFeature, SigmaMatch
from services.decision.classifier.incident_classifier import IncidentClassifier


async def run():
    classifier = IncidentClassifier()

    result = DetectionResult(
        id=uuid4(),
        event_id=uuid4(),
        entity_id="192.168.1.10",
        entity_type="ip",
        composite_score=0.82,
        individual_scores={"modelA": 0.8},
        contributing_models=["modelA"],
        shap_values=[
            SHAPFeature(
                feature_name="login_failures",
                human_label="Login Failures",
                shap_value=0.3,
                feature_value=10
            )
        ],
        sigma_matches=[],
        ttp_hints=["T1486"]
    )

    incident = await classifier.classify(result)
    print(incident)


asyncio.run(run())