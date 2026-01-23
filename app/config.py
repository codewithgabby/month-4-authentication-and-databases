import os

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

ALGORITHM = "HS256"

# Safety check (VERY IMPORTANT)
if not SECRET_KEY or not REFRESH_SECRET_KEY:
    raise RuntimeError("JWT secrets are not set")

# TODO:
# Refactor this config to use Pydantic BaseSettings after project completion
