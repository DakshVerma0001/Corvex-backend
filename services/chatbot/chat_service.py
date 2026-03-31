class ChatService:

    def generate_response(self, context: dict, question: str) -> str:

        if not context:
            return "Incident not found."

        incident = context["incident"]
        ttps = context["ttps"]
        actions = context["actions"]
        kill_chain = context["kill_chain"]

        question = question.lower()

        if "what happened" in question:
            return (
                f"This incident is classified as {incident['type']} with "
                f"{incident['severity']} severity. "
                f"It has a risk score of {incident['score']}."
            )

        if "why" in question:
            ttp_list = [t.get("technique_id") for t in ttps]
            return (
                f"The incident was flagged due to suspicious behavior mapped to "
                f"TTPs: {', '.join(ttp_list)}."
            )

        if "action" in question:
            if not actions:
                return "No actions have been executed for this incident."

            return "Actions taken: " + ", ".join(
                [a["action"] for a in actions]
            )

        if "kill chain" in question:
            return f"Predicted next steps: {', '.join(kill_chain)}"

        return "I can explain what happened, why it was flagged, actions taken, or kill chain."