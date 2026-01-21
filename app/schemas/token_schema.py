# schemas/token_schema.py
from pydantic import BaseModel, Field

class TokenPair(BaseModel):
    access_token: str = Field(..., description="Short-lived JWT access token")
    refresh_token: str = Field(..., description="Long-lived refresh token; store securely")
    token_type: str = Field("bearer", description="Token type to use in Authorization header")

    model_config = {"extra": "forbid"}  # disallow unexpected fields

class TokenOut(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")

    model_config = {"extra": "forbid"}
