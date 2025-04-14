"""
Pydantic models for authentication.
"""

from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    """Base user model."""

    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """User creation model."""

    password: str = Field(..., min_length=8)
    role: Optional[str] = Field("user", description="User role (default: user)")


class UserLogin(UserBase):
    """User login model."""

    password: str


class UserResponse(UserBase):
    """User response model."""

    role: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class Token(BaseModel):
    """Token response model."""

    token: str
    expires: str
