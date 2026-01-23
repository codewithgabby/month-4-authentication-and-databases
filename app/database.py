from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.user_model import User
from app.models.refresh_token_model import RefreshToken
from app.models.file_model import FileUpload

from app.db_base import Base


from app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False, 
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)
