from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import SeatStatus
from src.models import Seat


async def release_expired_temp_hold_seats(session: AsyncSession) -> int:
    try:
        now = datetime.now(UTC).replace(tzinfo=None)

        stmt = (
            update(Seat)
            .where(
                Seat.status == SeatStatus.TEMP_HOLD,
                Seat.hold_expires_at < now,
            )
            .values(
                status=SeatStatus.VACANT,
                user_id=None,
                hold_expires_at=None,
            )
        )

        result = await session.execute(stmt)
        await session.commit()

        return result.rowcount

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
