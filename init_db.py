import asyncio
from services.decision.db import engine, Base
from .services.decision.models import IncidentRow  # important import


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(init())