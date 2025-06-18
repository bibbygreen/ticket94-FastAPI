# src/seat_init/router.py

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.schemas import DetailResponse
from src.seat_init.schemas import CreateSectionRequest, InitializeSeatsRequest
from src.seat_init.service import (
    create_section_by_admin,
    initialize_seats_by_admin,
)

router = APIRouter(tags=["Seat Initialization"])


@router.post("/admin/events/{event_id}/sections", response_model=DetailResponse)
async def _create_section_by_admin(
    event_id: int,
    section_data: CreateSectionRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    try:
        await create_section_by_admin(session=session, event_id=event_id, section_data=section_data)

        return {"detail": "Section created successfully"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post(
    "/admin/sections/{section_id}/seats/init",
    response_model=DetailResponse,
)
async def _initialize_seats_by_admin(
    section_id: int,
    data: InitializeSeatsRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
):
    try:
        await initialize_seats_by_admin(session=session, section_id=section_id, data=data)

        return {"detail": "Seats initialized successfully"}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
