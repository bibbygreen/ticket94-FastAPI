from datetime import datetime, time

from fastapi import HTTPException, status
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.event.schemas import (
    CreateEventRequestByAdmin,
)
from src.models import (
    Event,
)


def make_naive(dt: datetime | time) -> datetime | time:
    if hasattr(dt, "tzinfo") and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


async def create_event_by_admin(
    session: AsyncSession,
    event_data: CreateEventRequestByAdmin,
):
    try:
        stmt = insert(Event).values(
            {
                "event_name": event_data.event_name,
                "description": event_data.description,
                "event_date": event_data.event_date,
                "event_time": make_naive(event_data.event_time),
                "sale_time": make_naive(event_data.sale_time),
                "sale_end_time": make_naive(event_data.sale_end_time),
                "location": event_data.location,
                "address": event_data.address,
                "organizer": event_data.organizer,
                "category": event_data.category,
                "on_sale": event_data.on_sale,
            }
        )
        await session.execute(stmt)
        await session.commit()

        return {"detail": "Event created successfully"}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
