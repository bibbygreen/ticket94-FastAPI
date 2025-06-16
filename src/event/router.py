from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_admin_user, get_current_user
from src.database import get_db_session
from src.event.schemas import (
    CreateEventRequestByAdmin,
    GetEventDetailByIdResponse,
)
from src.event.service import (
    create_event_by_admin,
    delete_event_by_admin,
    get_event_detail_by_id,
)
from src.models import User
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
    current_user: Annotated[User, Depends(get_admin_user)],
):
    try:
        await create_event_by_admin(
            session=session, event_data=event_data, current_user=current_user
        )
        return {"detail": "Event created successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get(
    "/event/{event_id}",
    response_model=GetEventDetailByIdResponse,
)
async def _get_event_detail_by_id(
    event_id: Annotated[int, Path()],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return await get_event_detail_by_id(session=session, event_id=event_id)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.delete(
    "/admin/event/{event_id}",
    response_model=DetailResponse,
)
async def _delete_event_by_admin(
    event_id: Annotated[int, Path()],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_admin_user)],
):
    try:
        await delete_event_by_admin(session=session, event_id=event_id, current_user=current_user)
        return {"detail": "Event deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
