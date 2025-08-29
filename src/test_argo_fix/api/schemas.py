"""API schemas for request/response models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# Base schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    """User schema with database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class User(UserInDB):
    """User schema for API responses."""

    pass


# Authentication schemas
class Token(BaseModel):
    """Token response schema."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema."""

    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str
    password: str


# Generic response schemas
class Message(BaseModel):
    """Generic message response."""

    message: str


class ErrorDetail(BaseModel):
    """Error detail schema."""

    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: ErrorDetail
