from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Seat, SeatingRow, Section, User
from src.seat_management.schemas import RowSeatResponse, SeatStatusResponse, SectionSeatMapResponse


async def get_seat_map_by_section(
    session: AsyncSession,
    section_id: int,
    current_user: User,
) -> SectionSeatMapResponse:
    try:
        section = await session.get(Section, section_id)
        if not section:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")

        rows_result = await session.execute(
            select(SeatingRow)
            .where(SeatingRow.section_id == section_id)
            .order_by(SeatingRow.row_order)
        )
        rows = rows_result.scalars().all()

        response_rows = []

        for row in rows:
            seats_result = await session.execute(
                select(Seat).where(Seat.row_id == row.row_id).order_by(Seat.seat_number)
            )
            seats = seats_result.scalars().all()

            response_seats = [
                SeatStatusResponse(
                    seat_id=seat.seat_id,
                    seat_number=seat.seat_number,
                    status=seat.status.value,
                )
                for seat in seats
            ]

            response_rows.append(
                RowSeatResponse(
                    row_name=row.row_name,
                    seats=response_seats,
                )
            )

        return SectionSeatMapResponse(
            section_id=section.section_id,
            rows=response_rows,
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
