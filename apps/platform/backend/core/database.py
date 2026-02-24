from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    # Disable asyncpg statement caching to work with pgbouncer transaction pooling
    connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0},
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
