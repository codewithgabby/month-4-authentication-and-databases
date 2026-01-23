import os

# ===============================
# Database
# ===============================
DATABASE_URL = os.environ.get("DATABASE_URL")

# ===============================
# Security
# ===============================
SECRET_KEY = os.environ.get("SECRET_KEY")
REFRESH_SECRET_KEY = os.environ.get("REFRESH_SECRET_KEY")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 10)
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", 7)
)

# ===============================
# Safety checks (VERY IMPORTANT)
# ===============================
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

if not REFRESH_SECRET_KEY:
    raise RuntimeError("REFRESH_SECRET_KEY is not set")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# TODO:
# Refactor this config to use Pydantic BaseSettings after project completion
