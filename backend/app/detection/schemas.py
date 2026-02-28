from datetime import datetime

from pydantic import BaseModel, Field


class DetectionMethodResponse(BaseModel):
    id: int = Field(..., description="Method ID", examples=[1])
    name: str = Field(..., description="Method name", examples=["safety_check_v1"])
    stage: int = Field(..., description="Pipeline stage this method belongs to", examples=[2])
    description: str = Field(..., description="Method description")
    usage_count: int = Field(..., description="Number of times this method has been used", examples=[150])
    decay_factor: float = Field(..., description="Current decay factor (1.0=full, 0.1=min)", examples=[0.85])
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {"from_attributes": True}


class ResetMethodsResponse(BaseModel):
    reset_count: int = Field(..., description="Number of methods reset", examples=[3])
    message: str = Field(..., description="Status message", examples=["All detection methods reset to full strength"])
