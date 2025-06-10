from datetime import timedelta
from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import CreateUserRequest, Token
from src.auth.service import (
    authenticate_user,
    create_access_token,
    create_user,
    get_user_by_account,
)
from src.config import settings
from src.database import get_db_session
from src.logger import logger

router = APIRouter(
    tags=["user"],
)


@router.post(
    "/v1/register",
    response_model=Token,
)
async def register(
    user_data: Annotated[CreateUserRequest, Body()],
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    try:
        db_user = await get_user_by_account(session=session, account=user_data.account)

        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
            )

        new_user = await create_user(session=session, user=user_data)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": new_user.account}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token)

    except Exception as exc:
        logger.exception(exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Register Error: {str(exc)}",
        ) from exc


@router.post(
    "/v1/login",
    response_model=Token,
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    try:
        user = authenticate_user(
            session=session, account=form_data.username, password=form_data.password
        )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": user.account}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token)

    except HTTPException as http_exc:
        logger.exception(http_exc)
        raise HTTPException(status_code=http_exc.status_code, detail=http_exc.detail) from http_exc
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"login error: {str(e)}",
        ) from e
