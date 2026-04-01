from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

Base = declarative_base()


# ✅ ADD THIS FUNCTION (CRITICAL)

async def save_incident_to_db(incident):
    async with AsyncSessionLocal() as session:
        try:
            # If you have ORM model, use it here
            # For now we just print (safe fallback)
            print("💾 Saving incident to DB:", incident)

            # TODO: Replace with actual ORM insert later
            # session.add(incident_model)
            # await session.commit()

        except Exception as e:
            print("❌ DB Error:", str(e))