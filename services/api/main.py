from fastapi import FastAPI, Depends
from fastapi.responses import Response
import asyncio  # NEW

from services.api.routers import incidents
from services.api.routers import auth

from services.api.dependencies.auth_dependency import get_current_user

from services.chatbot.context_builder import ContextBuilder
from services.chatbot.chat_service import ChatService
from services.chatbot.llm_service import LLMService
from services.chatbot.pdf_service import PDFService

# NEW: import consumer
from services.incident.consumer import start_consumer


def create_app() -> FastAPI:
    app = FastAPI(
        title="Cyber Response Platform API",
        version="1.0.0"
    )

    # -----------------------------
    # Routers (UNCHANGED)
    # -----------------------------
    app.include_router(auth.router, prefix="/api/v1/auth")
    app.include_router(incidents.router, prefix="/api/v1/incidents")

    # -----------------------------
    # Services (UNCHANGED)
    # -----------------------------
    context_builder = ContextBuilder()
    chat_service = ChatService()
    llm_service = LLMService()
    pdf_service = PDFService()

    # -----------------------------
    # ✅ START RABBITMQ CONSUMER (CRITICAL)
    # -----------------------------
    @app.on_event("startup")
    async def startup():
        print("🚀 Starting Incident Consumer...")
        asyncio.create_task(start_consumer())

    # -----------------------------
    # HEALTH CHECK
    # -----------------------------
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # -----------------------------
    # SECURED CHAT ENDPOINT
    # -----------------------------
    @app.get("/api/v1/chat/{incident_id}")
    async def chat(
        incident_id: str,
        question: str,
        user: str = Depends(get_current_user)
    ):
        print(f"\n=== CHAT ENDPOINT HIT by {user} ===")

        context = await context_builder.build(incident_id)

        print("Calling LLM...")
        response = llm_service.generate(context, question)

        if not response or response.startswith("LLM error"):
            print("Fallback triggered → using ChatService")
            response = chat_service.generate_response(context, question)

        return {"response": response}

    # -----------------------------
    # SECURED PDF EXPORT ENDPOINT
    # -----------------------------
    @app.get("/api/v1/incidents/{incident_id}/report")
    async def generate_report(
        incident_id: str,
        user: str = Depends(get_current_user)
    ):
        print(f"\n=== PDF GENERATION by {user} ===")

        context = await context_builder.build(incident_id)

        pdf_bytes = pdf_service.generate(context)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=incident_{incident_id}.pdf"
            }
        )

    return app


app = create_app()