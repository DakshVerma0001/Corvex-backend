import asyncio
from services.decision.db import engine
from sqlalchemy import text


async def test():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("DB Connected:", result.scalar())


asyncio.run(test())