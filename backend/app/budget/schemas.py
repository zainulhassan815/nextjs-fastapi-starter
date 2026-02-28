from pydantic import BaseModel, Field


class BudgetSummaryResponse(BaseModel):
    monthly_budget_usd: float = Field(..., description="Monthly budget limit in USD", examples=[175.0])
    spent_this_month_usd: float = Field(..., description="Total spent this month in USD", examples=[12.50])
    remaining_usd: float = Field(..., description="Remaining budget in USD", examples=[162.50])
    total_api_calls: int = Field(..., description="Total API calls this month", examples=[5000])
    cost_by_stage: dict[str, float] = Field(
        ..., description="Cost breakdown by stage", examples=[{"2": 8.50, "3": 4.00}]
    )
    budget_utilization_pct: float = Field(..., description="Budget utilization percentage", examples=[7.14])
