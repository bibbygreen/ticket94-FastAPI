from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_admin_user
from src.database import get_db_session
from src.models import User
from src.seat_maintenance.service import (
    release_expired_temp_hold_seats,
)

router = APIRouter(
    tags=["seat_maintenance"],
)


@router.post("/admin/seats/release-exxpired")
async def _release_expired_temp_hold_seats(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_admin_user)],
):
    try:
        released_count = await release_expired_temp_hold_seats(session=session)
        return {"released_seats": released_count}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
