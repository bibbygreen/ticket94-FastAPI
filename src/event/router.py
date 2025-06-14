from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.event.schemas import (
    CreateEventRequestByAdmin,
)
from src.event.service import (
    create_event_by_admin,
)
from src.schemas import (
    DetailResponse,
)

router = APIRouter(
    tags=["event"],
)


@router.post(
    "/admin/event",
    response_model=DetailResponse,
)
async def _create_event_by_admin(
    event_data: Annotated[CreateEventRequestByAdmin, Body()],
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    try:
        await create_event_by_admin(session=session, event_data=event_data)
        return {"detail": "Event created successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
