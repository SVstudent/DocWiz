"""Authentication schemas."""
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """User registration schema."""

    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    """Login response with token and user info."""

    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class TokenData(BaseModel):
    """Token payload data schema."""

    user_id: str
    email: str


class UserResponse(BaseModel):
    """User response schema."""

    id: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True
