from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.review.models import ReviewItem

REVIEW_BUDGET_PER_HOUR = 20


async def create_review_item(db: AsyncSession, post_id: int, reasoning: str) -> ReviewItem:
    """Add a post to the human review queue."""
    item = ReviewItem(post_id=post_id, ai_reasoning=reasoning)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def get_pending_reviews(db: AsyncSession) -> list[ReviewItem]:
    """Get all pending review items, oldest first."""
    result = await db.execute(
        select(ReviewItem).where(ReviewItem.status == "pending").order_by(ReviewItem.created_at.asc())
    )
    return list(result.scalars().all())


async def get_reviews_this_hour(db: AsyncSession) -> int:
    """Count how many reviews have been completed in the current hour."""
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    result = await db.execute(
        select(func.count(ReviewItem.id)).where(
            ReviewItem.status != "pending",
            ReviewItem.reviewed_at >= one_hour_ago,
        )
    )
    return result.scalar() or 0


async def submit_review(
    db: AsyncSession, post_id: int, reviewer_id: int, decision: str, note: str | None = None
) -> ReviewItem | None:
    """Submit a human review decision."""
    result = await db.execute(select(ReviewItem).where(ReviewItem.post_id == post_id, ReviewItem.status == "pending"))
    item = result.scalar_one_or_none()
    if not item:
        return None

    item.status = decision
    item.reviewer_id = reviewer_id
    item.review_note = note
    item.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(item)

    # Update the post status based on review decision
    from app.content.service import update_post_status

    new_status = "safe" if decision == "approved" else "harmful"
    await update_post_status(db, post_id, new_status)

    return item


async def get_review_budget(db: AsyncSession) -> dict:
    """Get the current hourly review budget status."""
    used = await get_reviews_this_hour(db)
    return {
        "reviews_this_hour": used,
        "budget_per_hour": REVIEW_BUDGET_PER_HOUR,
        "remaining": max(0, REVIEW_BUDGET_PER_HOUR - used),
    }
