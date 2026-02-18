import asyncio
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.client import Client
from sqlalchemy.sql import text

async def test_connection():
    print("--- Testing Supabase Connection ---")
    async with AsyncSessionLocal() as session:
        # 1. Test Simple Query
        try:
            result = await session.execute(text("SELECT 1"))
            print("✅ Connection Successful!")
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            return

        # 2. Test Write (Create Client)
        new_client = Client(name="Test Client", slug="test-client")
        session.add(new_client)
        try:
            await session.commit()
            print("✅ Created 'Test Client'")
        except Exception as e:
            await session.rollback()
            print(f"⚠️ Could not create client (might exist): {e}")

        # 3. Test Read
        result = await session.execute(select(Client).where(Client.name == "Test Client"))
        client = result.scalars().first()
        if client:
            print(f"✅ Verified Client: ID={client.id}, Name={client.name}, Created={client.created_at}")
        else:
            print("❌ Startling Error: Wrote client but cannot find it.")

if __name__ == "__main__":
    asyncio.run(test_connection())
