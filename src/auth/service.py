from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import CreateUserRequest
from src.auth.utils import get_password_hash, verify_password
from src.config import settings
from src.models import User


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_user_by_account(session: AsyncSession, account: str) -> User:
    query = select(User).where(User.account == account)
    result = await session.execute(query)
    user = result.scalar()

    return user


async def create_user(session: AsyncSession, user: CreateUserRequest) -> User:
    try:
        user.password = await get_password_hash(password=user.password)

        insert_query = (
            insert(User)
            .values(
                {
                    "account": user.account,
                    "password": user.password,
                }
            )
            .returning(User)
        )

        new_user = await session.execute(insert_query)

        await session.commit()

        return new_user.scalars().one()

    except Exception as e:
        session.rollback()
        raise e


async def authenticate_user(session: AsyncSession, account: str, password: str) -> User:
    db_user = await get_user_by_account(session=session, account=account)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not await verify_password(plain_password=password, hashed_password=db_user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password or account"
        )

    return db_user
