from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_user
from src.database import get_db_session
from src.models import User
from src.seat_management.schemas import (
    ConfirmSeatRequest,
    HoldSeatRequest,
    SectionSeatMapResponse,
)
from src.seat_management.service import (
    confirm_seats,
    get_seat_map_by_section,
    hold_seats,
    release_seats,
)

router = APIRouter(
    tags=["seat_management"],
)


@router.get(
    "/sections/{section_id}/seat_map",
    response_model=SectionSeatMapResponse,
)
async def _get_seat_map_by_section(
    section_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return await get_seat_map_by_section(
            session=session,
            section_id=section_id,
            current_user=current_user,
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/seats/hold")
async def _hold_seats(
    request: HoldSeatRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return await hold_seats(
            request=request,
            session=session,
            user_id=current_user.user_id,
            current_user=current_user,
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/seats/release")
async def _release_seat(
    request: HoldSeatRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return await release_seats(
            session=session,
            user_id=current_user.user_id,
            request=request,
            current_user=current_user,
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post("/seats/confirm")
async def _confirm_seat(
    request: ConfirmSeatRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return await confirm_seats(
            session=session,
            user_id=current_user.user_id,
            request=request,
            current_user=current_user,
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
