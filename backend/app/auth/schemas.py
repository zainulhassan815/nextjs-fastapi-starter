from pydantic import BaseModel, EmailStr, Field


class CreateUserRequest(BaseModel):
    """Request to register a new user."""

    email: EmailStr = Field(..., description="User email address", examples=["user@example.com"])
    password: str = Field(..., min_length=8, description="User password", examples=["strongpassword"])
    full_name: str | None = Field(None, max_length=255, description="User full name", examples=["John Doe"])


class LoginRequest(BaseModel):
    """Request to authenticate a user."""

    email: EmailStr = Field(..., description="User email address", examples=["user@example.com"])
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """JWT token response after successful authentication."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
