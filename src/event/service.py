from datetime import datetime, time

from fastapi import HTTPException, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.event.schemas import (
    CreateEventRequestByAdmin,
    GetEventDetailByIdResponse,
)
from src.models import (
    Event,
    EventPicture,
    EventTicketType,
    User,
)


def make_naive(dt: datetime | time) -> datetime | time:
    if hasattr(dt, "tzinfo") and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


async def create_event_by_admin(
    session: AsyncSession,
    event_data: CreateEventRequestByAdmin,
    current_user: User,
):
    try:
        result = await session.execute(
            insert(Event)
            .values(
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
            .returning(Event.event_id)
        )
        await session.flush()
        event_id = result.scalars().one()

        await session.execute(
            insert(EventPicture).values(
                {
                    "event_id": event_id,
                    "picture_url": event_data.picture_url,
                }
            )
        )

        if not event_data.ticket_types:
            raise HTTPException(status_code=400, detail="At least one ticket type is required")

        ticket_type_values = [
            {
                "event_id": event_id,
                "ticket_name": ticket.ticket_name,
                "max_purchase_limit": ticket.max_purchase_limit,
                "price": ticket.price,
                "stock": ticket.stock,
            }
            for ticket in event_data.ticket_types
        ]

        await session.execute(insert(EventTicketType).values(ticket_type_values))

        await session.commit()

        return {"detail": "Event created successfully"}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


async def get_event_detail_by_id(
    session: AsyncSession,
    event_id: int,
    current_user: User,
) -> GetEventDetailByIdResponse:
    try:
        stmt = (
            select(
                Event.event_id,
                Event.event_name,
                Event.description,
                Event.event_date,
                Event.event_time,
                Event.sale_time,
                Event.sale_end_time,
                Event.location,
                Event.address,
                Event.organizer,
                Event.on_sale,
                Event.category,
                EventPicture.picture_url,
            )
            .join(EventPicture, Event.event_id == EventPicture.event_id)
            .where(Event.event_id == event_id)
        )
        result = await session.execute(stmt)
        data = result.mappings().one()

        event = GetEventDetailByIdResponse(**data)

        return event

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


async def delete_event_by_admin(
    session: AsyncSession,
    event_id: int,
    current_user: User,
):
    try:
        await session.execute(
            update(Event).values(is_deleted=True).where(Event.event_id == event_id)
        )

        await session.execute(delete(EventPicture).where(EventPicture.event_id == event_id))
        await session.commit()
        return {"detail": "Event deleted successfully"}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
