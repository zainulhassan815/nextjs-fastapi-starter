from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from sqlalchemy import select

from app.content import service as content_service
from app.content.models import Post
from app.content.schemas import ContentStatsResponse, CreatePostRequest, PostResponse
from app.deps import CurrentUserDep, DbDep
from app.schemas.base import ErrorResponse

router = APIRouter()


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
    description="Submit a new post for content moderation. Language is auto-detected if not provided.",
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def create_post(
    body: CreatePostRequest, current_user: CurrentUserDep, db: DbDep, background_tasks: BackgroundTasks
):
    post = await content_service.create_post(
        db, content=body.content, author_id=current_user.id, language=body.language
    )
    # Import here to avoid circular imports — moderation pipeline runs in background
    from app.moderation.service import run_moderation_pipeline

    background_tasks.add_task(run_moderation_pipeline, post.id)
    return post


@router.post(
    "/moderate-pending",
    response_model=dict,
    summary="Moderate all pending posts",
    description="Trigger the moderation pipeline on all posts with 'pending' status",
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def moderate_pending_posts(
    db: DbDep, current_user: CurrentUserDep, background_tasks: BackgroundTasks
):
    from app.moderation.service import run_moderation_pipeline

    result = await db.execute(select(Post).where(Post.status == "pending"))
    pending_posts = list(result.scalars().all())
    for post in pending_posts:
        background_tasks.add_task(run_moderation_pipeline, post.id)
    return {"queued": len(pending_posts)}


@router.get(
    "/",
    response_model=list[PostResponse],
    summary="List posts",
    description="Get a list of posts ordered by most recent",
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def list_posts(db: DbDep, current_user: CurrentUserDep, limit: int = 50, offset: int = 0):
    return await content_service.list_posts(db, limit=limit, offset=offset)


@router.get(
    "/stats",
    response_model=ContentStatsResponse,
    summary="Get content statistics",
    description="Get aggregate statistics about posts by status and language",
    responses={401: {"model": ErrorResponse, "description": "Not authenticated"}},
)
async def get_content_stats(db: DbDep, current_user: CurrentUserDep):
    stats = await content_service.get_content_stats(db)
    return stats


@router.post(
    "/{post_id}/escalate",
    response_model=PostResponse,
    summary="Manually escalate a post",
    description="Force-escalate a post to the human review queue",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def escalate_post(post_id: int, db: DbDep, current_user: CurrentUserDep):
    post = await content_service.get_post(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Post not found"},
        )
    post.status = "escalated"
    await db.commit()
    await db.refresh(post)

    from app.review.service import create_review_item

    await create_review_item(
        db, post_id=post.id, reasoning="Manually escalated by moderator",
    )
    return post


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Get a post",
    description="Get a single post by ID",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Post not found"},
    },
)
async def get_post(post_id: int, db: DbDep, current_user: CurrentUserDep):
    post = await content_service.get_post(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Post not found"},
        )
    return post
