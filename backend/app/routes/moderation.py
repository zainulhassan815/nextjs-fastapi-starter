from fastapi import APIRouter, HTTPException, status

from app.content.service import get_post
from app.deps import CurrentUserDep, DbDep
from app.moderation.schemas import PostModerationResponse
from app.moderation.service import get_moderation_results
from app.schemas.base import ErrorResponse

router = APIRouter()


@router.get(
    "/{post_id}/results",
    response_model=PostModerationResponse,
    summary="Get moderation results",
    description="Get all moderation pipeline results for a specific post",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def get_post_moderation(post_id: int, db: DbDep, current_user: CurrentUserDep):
    post = await get_post(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Post not found"},
        )
    results = await get_moderation_results(db, post_id)
    return PostModerationResponse(
        post_id=post.id,
        current_status=post.status,
        results=results,
    )
