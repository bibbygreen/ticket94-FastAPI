import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.auth.dependencies import get_current_user
from src.config import settings
from src.constants import Role
from src.main import app
from src.models import User

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=True,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def override_get_admin_user():
    return User(
        user_id=1000,
        account="test_admin_override",
        password="1234",
        role=Role.ADMIN.value,
    )


app.dependency_overrides[get_current_user] = override_get_admin_user


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            session.add_all(
                [
                    User(
                        user_id=1000,
                        account="test_admin",
                        password="1234",
                        role=Role.ADMIN.value,
                    ),
                ]
            )
            await session.commit()

    yield

    async with AsyncSessionLocal() as session:
        async with session.begin():
            delete_user_query = delete(User).where(User.user_id.in_([1000, 1001, 1002]))
            await session.execute(delete_user_query)
            await session.commit()


@pytest_asyncio.fixture(loop_scope="session")
async def client():
    host, port = "127.0.0.1", "8000"

    async with AsyncClient(
        transport=ASGITransport(app=app, client=(host, port)), base_url="http://test"
    ) as client:
        yield client
