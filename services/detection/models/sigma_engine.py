import structlog

logger = structlog.get_logger()


class SigmaRule:
    def __init__(self, rule_id, rule_name, condition, ttp_tags, severity):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.condition = condition
        self.ttp_tags = ttp_tags
        self.severity = severity


class SigmaEngine:
    def __init__(self):
        self.rules = self.load_rules()

    def load_rules(self):
        # Hardcoded rules (later YAML se load karenge)
        return [
            SigmaRule(
                rule_id="SIGMA-001",
                rule_name="Brute Force Login",
                condition=lambda e: e.get("event_outcome") == "failure",
                ttp_tags=["T1110"],
                severity="HIGH"
            ),
            SigmaRule(
                rule_id="SIGMA-002",
                rule_name="Suspicious Admin Command",
                condition=lambda e: e.get("process_name") == "vssadmin",
                ttp_tags=["T1490"],
                severity="CRITICAL"
            )
        ]

    def evaluate(self, event):
        matches = []

        for rule in self.rules:
            try:
                if rule.condition(event):
                    matches.append({
                        "rule_id": rule.rule_id,
                        "rule_name": rule.rule_name,
                        "ttp_tags": rule.ttp_tags,
                        "severity": rule.severity
                    })
            except Exception as e:
                logger.error("sigma_rule_error", error=str(e))

        return matches