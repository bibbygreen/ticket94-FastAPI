from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.database import get_db_session
from src.seat_maintenance.service import release_expired_temp_hold_seats

scheduler = AsyncIOScheduler()


def start_seat_cleanup_scheduler():
    scheduler.add_job(
        func=_run_release_seat_task,
        trigger=IntervalTrigger(seconds=60),
        id="release_seat_task",
        replace_existing=True,
    )
    scheduler.start()


async def _run_release_seat_task():
    gen = get_db_session()
    session = await anext(gen)

    try:
        released_count = await release_expired_temp_hold_seats(session=session)
        print(f"[Scheduler] Released {released_count} expired held seats.")
    except Exception as e:
        print(f"[Scheduler] Error releasing seats: {e}")
    finally:
        await gen.aclose()
