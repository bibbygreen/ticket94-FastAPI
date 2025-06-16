from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from jose import jwt
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import CreateUserRequest
from src.auth.utils import get_password_hash, verify_password
from src.config import settings
from src.constants import Role
from src.logger import logger
from src.models import User


def create_access_token(data: dict, expires_delta: timedelta | None = None):
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


async def authenticate_user(session: AsyncSession, account: str, password: str) -> User:
    db_user = await get_user_by_account(session=session, account=account)

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not await verify_password(plain_password=password, hashed_password=db_user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password or account"
        )

    return db_user


async def create_admin_user(session: AsyncSession, user: CreateUserRequest) -> User:
    try:
        user.password = await get_password_hash(password=user.password)

        insert_query = insert(User).values(
            {
                "account": user.account,
                "password": user.password,
                "role": Role.ADMIN.value,
            }
        )

        await session.execute(insert_query)
        await session.commit()

        stmt = select(User.account).where(User.account == user.account)
        result = await session.execute(stmt)
        new_user = result.scalar_one()

        return new_user

    except Exception as e:
        await session.rollback()
        logger.exception("Failed to create user: %s", str(e))
        raise e


async def create_customer_user(
    session: AsyncSession,
    user: CreateUserRequest,
) -> User:
    try:
        # 檢查帳號是否已存在
        stmt = select(User).where(User.account == user.account)
        existing_user = (await session.execute(stmt)).scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "ACCUNT_ALREADY_EXISTS",
                    "message": "Account {user.account} already exists.。",
                },
            )

        user.password = await get_password_hash(password=user.password)

        insert_query = insert(User).values(
            {
                "account": user.account,
                "password": user.password,
                "role": Role.GUEST.value,
            }
        )

        await session.execute(insert_query)
        await session.commit()

        stmt = select(User.account).where(User.account == user.account)
        result = await session.execute(stmt)
        new_user = result.scalar_one()

        return new_user

    except Exception as e:
        await session.rollback()
        logger.exception("Failed to create user: %s", str(e))
        raise e
