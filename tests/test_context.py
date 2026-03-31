import asyncio
from services.chatbot.context_builder import ContextBuilder


async def main():
    builder = ContextBuilder()

    incident_id = input("Enter Incident ID: ")

    context = await builder.build(incident_id)

    print(context)


asyncio.run(main())