import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.auth.router import router as user_router
from src.config import settings
from src.constants import DEFAULT_ERROR_RESPONSE
from src.event.router import router as event_router
from src.logger import logger
from src.order.router import router as order_router
from src.schedule import start_seat_cleanup_scheduler
from src.seat_init.router import router as seat_init_router
from src.seat_maintenance.router import router as seat_maintenance_router
from src.seat_management.router import router as seat_management_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting application")

        start_seat_cleanup_scheduler()
        logger.info("Seat cleanup scheduler started.")

    except Exception as e:
        logger.exception(f"run_migrations failed, error: {e}")
    yield


app = FastAPI(
    root_path="/api",
    lifespan=lifespan,
    docs_url="/docs" if settings.MODE == "dev" else None,
    redoc_url="/redoc" if settings.MODE == "dev" else None,
    responses=DEFAULT_ERROR_RESPONSE,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(user_router)
app.include_router(event_router)
app.include_router(seat_init_router)
app.include_router(seat_management_router)
app.include_router(order_router)
app.include_router(seat_maintenance_router)
