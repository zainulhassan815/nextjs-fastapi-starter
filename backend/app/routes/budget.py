from fastapi import APIRouter

from app.budget.schemas import BudgetSummaryResponse
from app.budget.service import get_budget_summary
from app.deps import CurrentUserDep, DbDep
from app.schemas.base import ErrorResponse

router = APIRouter()


@router.get(
    "/summary",
    response_model=BudgetSummaryResponse,
    summary="Get budget summary",
    description="Get the current monthly API cost budget summary with breakdown by stage",
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def get_budget(db: DbDep, current_user: CurrentUserDep):
    return await get_budget_summary(db)
