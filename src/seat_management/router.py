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
    SectionSeatMapResponse,
)
from src.seat_management.service import (
    get_seat_map_by_section,
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
