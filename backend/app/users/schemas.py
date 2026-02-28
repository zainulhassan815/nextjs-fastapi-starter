from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """User profile response."""

    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    full_name: str | None = Field(None, description="User full name")
    is_active: bool = Field(..., description="Whether user account is active")

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    """Request to update user profile."""

    full_name: str | None = Field(None, max_length=255, description="Updated full name")
    email: EmailStr | None = Field(None, description="Updated email address")
