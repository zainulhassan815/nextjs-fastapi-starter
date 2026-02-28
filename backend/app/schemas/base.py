from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response format."""

    code: str = Field(..., description="Machine-readable error code", examples=["VALIDATION_ERROR"])
    message: str = Field(..., description="Human-readable error message", examples=["Invalid input"])
    details: dict | None = Field(None, description="Additional error context")


class PaginationMeta(BaseModel):
    """Pagination information for list responses."""

    total: int = Field(..., description="Total number of items", examples=[100])
    page: int = Field(..., description="Current page number", examples=[1])
    per_page: int = Field(..., description="Items per page", examples=[20])
    total_pages: int = Field(..., description="Total number of pages", examples=[5])


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response."""

    data: list[T]
    meta: PaginationMeta
