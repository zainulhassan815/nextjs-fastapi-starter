from datetime import datetime

from pydantic import BaseModel, Field


class CreatePostRequest(BaseModel):
    content: str = Field(
        ..., min_length=1, max_length=10000, description="Post content text", examples=["This is a sample post"]
    )
    language: str | None = Field(
        None, description="Language override (auto-detected if not provided)", examples=["english"]
    )


class PostResponse(BaseModel):
    id: int = Field(..., description="Post ID", examples=[1])
    content: str = Field(..., description="Post content text")
    language: str = Field(..., description="Detected language", examples=["english"])
    status: str = Field(..., description="Moderation status", examples=["pending"])
    author_id: int = Field(..., description="Author user ID", examples=[1])
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class ContentStatsResponse(BaseModel):
    total_posts: int = Field(..., description="Total number of posts", examples=[100])
    by_status: dict[str, int] = Field(
        ..., description="Post counts by status", examples=[{"safe": 50, "harmful": 10, "pending": 40}]
    )
    by_language: dict[str, int] = Field(
        ..., description="Post counts by language", examples=[{"english": 60, "urdu": 30, "roman_urdu": 10}]
    )
    recent_posts: list[PostResponse] = Field(..., description="Most recent posts")
