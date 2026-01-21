# schemas/user_schema.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=72, description="Plain password (will be hashed). Minimum 8 characters.")
    full_name: Optional[str] = Field(None, description="Full name")

   
    model_config = {"extra": "forbid"}


class UserResponse(BaseModel):
    id: int = Field(..., description="User id")
    email: EmailStr = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="Full name")
    role: str = Field(..., description="Role (user/admin)")
    is_active: bool = Field(..., description="Is user active?")

    # Pydantic v2 way to read attributes from ORM objects (like SQLAlchemy)
    model_config = {"from_attributes": True, "extra": "forbid"}


