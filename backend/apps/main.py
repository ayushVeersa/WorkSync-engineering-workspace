import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from apps.api.auth import router as auth_router
from apps.api.employee import router as employee_router
from apps.api.department import router as department_router
from apps.api.project import router as project_router
from apps.api.employee_project import router as emp_proj_router
from apps.api.issue import router as issue_router
from apps.api.comment import router as comment_router
from apps.api.dashboard import router as dashboard_router
from apps.api.attachment import router as attachment_router

from apps.core.logging import get_logger

logger = get_logger(__name__)

# added lifespan to log startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")


app = FastAPI(lifespan=lifespan)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log every incoming HTTP request and its response.
    """
    start_time = time.perf_counter()
    client = request.client.host if request.client else "unknown"
    logger.info(
        "REQUEST  %s %s from %s",
        request.method,
        request.url.path,
        client,
    )

    response = None
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception(
            "UNHANDLED ERROR processing %s %s: %s",
            request.method,
            request.url.path,
            exc,
        )
        raise
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000
        if response is not None:
            logger.info(
                "RESPONSE %s %s -> %s (%.2f ms)",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )
        else:
            logger.info(
                "RESPONSE %s %s -> ERROR (%.2f ms)",
                request.method,
                request.url.path,
                duration_ms,
            )

    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception for %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


app.include_router(auth_router)
app.include_router(employee_router)
app.include_router(department_router)
app.include_router(project_router)
app.include_router(emp_proj_router)
app.include_router(issue_router)
app.include_router(comment_router)
app.include_router(dashboard_router)
app.include_router(attachment_router)


@app.get("/health")
def check_health():
    logger.info("Health check requested")
    return {"Health": "OK"}
