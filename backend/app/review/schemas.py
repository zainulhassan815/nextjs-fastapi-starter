from datetime import datetime

from pydantic import BaseModel, Field


class ReviewItemResponse(BaseModel):
    id: int = Field(..., description="Review item ID", examples=[1])
    post_id: int = Field(..., description="Post ID", examples=[1])
    ai_reasoning: str = Field(..., description="AI reasoning for escalation")
    status: str = Field(..., description="Review status", examples=["pending"])
    reviewer_id: int | None = Field(None, description="Reviewer user ID")
    review_note: str | None = Field(None, description="Reviewer's note")
    created_at: datetime = Field(..., description="When the item was queued")
    reviewed_at: datetime | None = Field(None, description="When the review was completed")

    model_config = {"from_attributes": True}


class SubmitReviewRequest(BaseModel):
    post_id: int = Field(..., description="Post ID to review", examples=[1])
    decision: str = Field(..., description="Review decision: approved or rejected", examples=["approved"])
    note: str | None = Field(
        None,
        max_length=1000,
        description="Optional reviewer note",
        examples=["Content is satirical, not harmful"],
    )


class ReviewBudgetResponse(BaseModel):
    reviews_this_hour: int = Field(..., description="Reviews completed in the current hour", examples=[5])
    budget_per_hour: int = Field(..., description="Maximum reviews allowed per hour", examples=[20])
    remaining: int = Field(..., description="Reviews remaining this hour", examples=[15])
