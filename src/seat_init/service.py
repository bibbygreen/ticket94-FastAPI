from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Event, Seat, SeatingRow, Section
from src.seat_init.schemas import CreateSectionRequest, InitializeSeatsRequest


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


async def initialize_seats_by_admin(
    section_id: int,
    data: InitializeSeatsRequest,
    session: AsyncSession,
):
    try:
        section = await session.get(Section, section_id)
        if not section:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

        existing_rows_result = await session.execute(
            select(SeatingRow).where(SeatingRow.section_id == section_id)
        )
        if existing_rows_result.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seats have already been initialized for this section",
            )

        for row_data in data.rows:
            seating_row = SeatingRow(
                section_id=section_id,
                row_name=row_data.row_name,
            )
            session.add(seating_row)
            await session.flush()  # 拿到 row_id

            seats = [
                Seat(row_id=seating_row.row_id, seat_number=str(i + 1).zfill(2))
                for i in range(row_data.seat_count)
            ]
            session.add_all(seats)

        await session.commit()

        return {"detail": "Seats initialized successfully"}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
