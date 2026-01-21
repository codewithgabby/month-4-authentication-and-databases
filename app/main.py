from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.logging_config import setup_logging
import logging

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.rate_limiter import limiter
from app.routers import auth_router, admin_router, user_router, file_router

setup_logging()
logger = logging.getLogger("app")

app = FastAPI(title="TokenSafe - JWT + Refresh + RBAC")

logger.info("Starting TokenSafe application")

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Custom rate-limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please slow down."
        },
    )

# Include routers
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(admin_router.router)
app.include_router(file_router.router)
