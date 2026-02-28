from datetime import datetime

from pydantic import BaseModel, Field


class ModerationResultResponse(BaseModel):
    id: int = Field(..., description="Result ID", examples=[1])
    post_id: int = Field(..., description="Post ID", examples=[1])
    stage: int = Field(..., description="Pipeline stage (1, 2, or 3)", examples=[2])
    method_name: str | None = Field(None, description="Detection method used", examples=["safety_check_v1"])
    verdict: str = Field(..., description="Moderation verdict", examples=["safe"])
    confidence: float = Field(..., description="Confidence score 0-1", examples=[0.95])
    reasoning: str | None = Field(None, description="Explanation of the verdict")
    cost_usd: float = Field(..., description="Cost of this analysis in USD", examples=[0.0002])
    created_at: datetime = Field(..., description="When this result was created")

    model_config = {"from_attributes": True}


class PostModerationResponse(BaseModel):
    post_id: int = Field(..., description="Post ID")
    current_status: str = Field(..., description="Current post status", examples=["safe"])
    results: list[ModerationResultResponse] = Field(..., description="All moderation results for this post")
