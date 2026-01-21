from pydantic import BaseModel
from datetime import datetime

class FileResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}
