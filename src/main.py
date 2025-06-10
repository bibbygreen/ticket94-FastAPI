import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.auth.router import router as user_router
from src.config import settings
from src.constants import DEFAULT_ERROR_RESPONSE
from src.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting application")
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
