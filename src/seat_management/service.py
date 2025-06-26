from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import SeatStatus
from src.models import Seat, SeatingRow, Section, User
from src.seat_management.schemas import (
    ConfirmSeatRequest,
    HoldSeatRequest,
    ReleaseSeatRequest,
    RowSeatResponse,
    SeatStatusResponse,
    SectionSeatMapResponse,
)


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
                    status=seat.status,
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


async def hold_seats(
    request: HoldSeatRequest,
    session: AsyncSession,
    user_id: int,
    current_user: User,
):
    try:
        now = datetime.now(UTC).replace(tzinfo=None)
        hold_until = now + timedelta(minutes=10)

        result = await session.execute(
            select(Seat)
            .where(Seat.seat_id.in_(request.seat_ids))
            .with_for_update()  # 加鎖，避免多人同時搶位
        )
        seats = result.scalars().all()

        if len(seats) != len(request.seat_ids):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid seat IDs")

        for seat in seats:
            if seat.status != SeatStatus.VACANT:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Seat {seat.seat_number} is already reserved or held",
                )

            seat.status = SeatStatus.TEMP_HOLD
            seat.user_id = user_id
            seat.hold_expires_at = hold_until

            if seat.hold_expires_at < now:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Seat {seat.seat_id} is already reserved or held",
                )

        await session.commit()
        return {"detail": "Seats held successfully", "hold_until": hold_until}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


async def release_seats(
    session: AsyncSession,
    user_id: int,
    request: ReleaseSeatRequest,
    current_user: User,
):
    try:
        result = await session.execute(
            select(Seat)
            .where(Seat.seat_id.in_(request.seat_ids), Seat.user_id == user_id)
            .with_for_update()
        )
        seats = result.scalars().all()

        for seat in seats:
            if seat.status == SeatStatus.TEMP_HOLD:
                seat.status = SeatStatus.VACANT
                seat.hold_expires_at = None
                seat.user_id = None

        await session.commit()
        return {"detail": "Seats released successfully"}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


async def confirm_seats(
    session: AsyncSession, user_id: int, request: ConfirmSeatRequest, current_user: User
):
    try:
        now = datetime.now()

        result = await session.execute(
            select(Seat)
            .where(Seat.seat_id.in_(request.seat_ids), Seat.user_id == user_id)
            .with_for_update()
        )
        seats = result.scalars().all()

        if len(seats) != len(request.seat_ids):
            raise HTTPException(status_code=400, detail="Some seats not belong to user")

        for seat in seats:
            if seat.status != SeatStatus.TEMP_HOLD or seat.hold_expires_at < now:
                raise HTTPException(
                    status_code=400, detail=f"Seat {seat.seat_number} cannot be confirmed"
                )
            seat.status = SeatStatus.RESERVED

        await session.commit()
        return {"detail": "Seats confirmed successfully"}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
