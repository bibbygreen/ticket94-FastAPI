from collections.abc import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

if settings.MODE == "dev":
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=True,
    )
else:
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=50,
        max_overflow=100,
        pool_pre_ping=True,
    )


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    future=True,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis_client() -> Redis:
    pool = ConnectionPool.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", decode_responses=True
    )

    return Redis.from_pool(pool)
