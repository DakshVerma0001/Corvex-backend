from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


class PDFService:

    def generate(self, context: dict) -> bytes:

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)

        styles = getSampleStyleSheet()
        elements = []

        incident = context.get("incident", {})

        elements.append(Paragraph("Incident Report", styles["Title"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Severity: {incident.get('severity')}", styles["Normal"]))
        elements.append(Paragraph(f"Type: {incident.get('type')}", styles["Normal"]))
        elements.append(Paragraph(f"Score: {incident.get('score')}", styles["Normal"]))
        elements.append(Paragraph(f"Autonomy Level: {incident.get('autonomy_level')}", styles["Normal"]))

        elements.append(Spacer(1, 12))

        elements.append(Paragraph("TTPs:", styles["Heading2"]))
        for ttp in context.get("ttps", []):
            elements.append(Paragraph(str(ttp), styles["Normal"]))

        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Actions Taken:", styles["Heading2"]))
        for action in context.get("actions", []):
            elements.append(Paragraph(str(action), styles["Normal"]))

        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Mitigation Plan:", styles["Heading2"]))
        elements.append(Paragraph(
            "Immediate isolation, block malicious entities, rotate credentials, and monitor system activity.",
            styles["Normal"]
        ))

        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        return pdf