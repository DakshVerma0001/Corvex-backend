import os
from groq import Groq
from dotenv import load_dotenv

# Load .env
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class LLMService:

    def generate(self, context: dict, question: str) -> str:

        if not context:
            return "Incident not found."

        # Clean data
        clean_ttps = [t.get("technique_id") for t in context.get("ttps", [])]
        clean_actions = [a.get("action") for a in context.get("actions", [])]

        prompt = f"""
You are a cybersecurity incident response assistant.

Explain clearly and professionally.

Incident Details:
- Severity: {context['incident']['severity']}
- Type: {context['incident']['type']}
- Score: {context['incident']['score']}
- Autonomy Level: {context['incident']['autonomy_level']}

MITRE Techniques: {clean_ttps}
Kill Chain Prediction: {context.get('kill_chain', [])}
Actions Taken: {clean_actions}

User Question:
{question}

Answer:
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",   # ✅ FIXED MODEL
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            print("LLM RAW RESPONSE:", response)

            if not response or not response.choices:
                return "LLM error: empty response"

            content = response.choices[0].message.content

            if not content:
                return "LLM error: no content"

            return content.strip()

        except Exception as e:
            print("LLM ERROR:", str(e))
            return f"LLM error: {str(e)}"