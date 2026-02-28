from fastapi import APIRouter, HTTPException, status

from app.deps import CurrentUserDep, DbDep
from app.review.schemas import ReviewBudgetResponse, ReviewItemResponse, SubmitReviewRequest
from app.review.service import get_pending_reviews, get_review_budget, get_reviews_this_hour, submit_review
from app.schemas.base import ErrorResponse

REVIEW_BUDGET_PER_HOUR = 20

router = APIRouter()


@router.get(
    "/queue",
    response_model=list[ReviewItemResponse],
    summary="Get review queue",
    description="Get all pending items in the human review queue",
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def get_review_queue(db: DbDep, current_user: CurrentUserDep):
    return await get_pending_reviews(db)


@router.post(
    "/",
    response_model=ReviewItemResponse,
    summary="Submit a review",
    description="Submit a human review decision for an escalated post. Enforces 20 reviews/hour budget.",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Review item not found"},
        429: {"model": ErrorResponse, "description": "Hourly review budget exceeded"},
    },
)
async def submit_review_decision(body: SubmitReviewRequest, db: DbDep, current_user: CurrentUserDep):
    # Check hourly budget
    used = await get_reviews_this_hour(db)
    if used >= REVIEW_BUDGET_PER_HOUR:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "BUDGET_EXCEEDED", "message": "Hourly review budget exceeded (20/hr)"},
        )
    item = await submit_review(
        db,
        post_id=body.post_id,
        reviewer_id=current_user.id,
        decision=body.decision,
        note=body.note,
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "No pending review found for this post"},
        )
    return item


@router.get(
    "/budget",
    response_model=ReviewBudgetResponse,
    summary="Get review budget",
    description="Get the current hourly review budget status",
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def get_budget(db: DbDep, current_user: CurrentUserDep):
    return await get_review_budget(db)
