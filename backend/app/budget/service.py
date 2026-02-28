from datetime import datetime, timezone

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.budget.models import CostLog

MONTHLY_BUDGET_USD = 175.0


async def log_cost(db: AsyncSession, cost_usd: float, stage: int, post_id: int) -> CostLog:
    """Log a cost entry for an API call."""
    entry = CostLog(post_id=post_id, stage=stage, cost_usd=cost_usd)
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_monthly_spend(db: AsyncSession) -> float:
    """Get total spend for the current month."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(func.coalesce(func.sum(CostLog.cost_usd), 0.0)).where(
            extract("year", CostLog.created_at) == now.year,
            extract("month", CostLog.created_at) == now.month,
        )
    )
    return float(result.scalar() or 0.0)


async def check_budget_remaining(db: AsyncSession) -> bool:
    """Check if there is budget remaining for AI calls."""
    spent = await get_monthly_spend(db)
    return spent < MONTHLY_BUDGET_USD


async def get_budget_summary(db: AsyncSession) -> dict:
    """Get comprehensive budget summary."""
    now = datetime.now(timezone.utc)
    month_filter = [
        extract("year", CostLog.created_at) == now.year,
        extract("month", CostLog.created_at) == now.month,
    ]

    # Total spend
    spent = await get_monthly_spend(db)

    # Total API calls this month
    calls_result = await db.execute(select(func.count(CostLog.id)).where(*month_filter))
    total_calls = calls_result.scalar() or 0

    # Cost by stage
    stage_result = await db.execute(
        select(CostLog.stage, func.sum(CostLog.cost_usd)).where(*month_filter).group_by(CostLog.stage)
    )
    cost_by_stage = {str(stage): round(cost, 6) for stage, cost in stage_result.all()}

    return {
        "monthly_budget_usd": MONTHLY_BUDGET_USD,
        "spent_this_month_usd": round(spent, 6),
        "remaining_usd": round(MONTHLY_BUDGET_USD - spent, 6),
        "total_api_calls": total_calls,
        "cost_by_stage": cost_by_stage,
        "budget_utilization_pct": round((spent / MONTHLY_BUDGET_USD) * 100, 2),
    }
