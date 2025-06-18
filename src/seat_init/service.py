from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Event, Section
from src.seat_init.schemas import CreateSectionRequest


async def create_section_by_admin(
    session: AsyncSession,
    event_id: int,
    section_data: CreateSectionRequest,
):
    try:
        event = await session.get(Event, event_id)
        if not event:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        section = Section(
            event_id=event_id,
            name=section_data.name,
            ticket_type_id=section_data.ticket_type_id,
            sort_order=section_data.sort_order,
        )

        session.add(section)
        await session.commit()

        return {"detail": "Section created successfully"}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
