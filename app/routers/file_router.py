from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

import os
import shutil
from uuid import uuid4

from app.database import get_db
from app.dependencies import get_current_user
from app.models.file_model import FileUpload
from app.schemas.file_schema import FileResponse

router = APIRouter(prefix="/files", tags=["Files"])

UPLOAD_DIR = "uploads"

# Create uploads folder if not exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    data: dict = Depends(get_current_user)
):
    user = data["user"]

    # Generate safe unique filename
    file_ext = file.filename.split(".")[-1]
    safe_filename = f"{uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save file info to DB
    db_file = FileUpload(
        filename=safe_filename,
        file_type=file.content_type,
        owner_id=user.id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return db_file




