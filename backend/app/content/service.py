import re

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.content.models import Post

# Urdu Unicode range
URDU_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")
# Common Roman Urdu markers
ROMAN_URDU_MARKERS = {
    "hai",
    "nahi",
    "yeh",
    "kya",
    "hain",
    "mein",
    "aur",
    "ko",
    "ka",
    "ki",
    "se",
    "ho",
    "tha",
    "thi",
    "raha",
    "wala",
    "kuch",
    "bohut",
    "bahut",
    "achi",
    "bura",
    "sab",
    "log",
    "ap",
    "tum",
    "yaar",
    "bhai",
}


def detect_language(text: str) -> str:
    # Check for Urdu script characters
    urdu_chars = len(URDU_PATTERN.findall(text))
    if urdu_chars > len(text) * 0.3:
        return "urdu"
    # Check for Roman Urdu markers
    words = set(text.lower().split())
    roman_urdu_hits = len(words & ROMAN_URDU_MARKERS)
    if roman_urdu_hits >= 2:
        return "roman_urdu"
    return "english"


async def create_post(db: AsyncSession, content: str, author_id: int, language: str | None = None) -> Post:
    detected_language = language or detect_language(content)
    post = Post(content=content, language=detected_language, author_id=author_id, status="pending")
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


async def get_post(db: AsyncSession, post_id: int) -> Post | None:
    result = await db.execute(select(Post).where(Post.id == post_id))
    return result.scalar_one_or_none()


async def list_posts(db: AsyncSession, limit: int = 50, offset: int = 0) -> list[Post]:
    result = await db.execute(select(Post).order_by(Post.created_at.desc()).limit(limit).offset(offset))
    return list(result.scalars().all())


async def update_post_status(db: AsyncSession, post_id: int, status: str) -> Post | None:
    post = await get_post(db, post_id)
    if not post:
        return None
    post.status = status
    await db.commit()
    await db.refresh(post)
    return post


async def get_content_stats(db: AsyncSession) -> dict:
    # Total
    total_result = await db.execute(select(func.count(Post.id)))
    total = total_result.scalar() or 0
    # By status
    status_result = await db.execute(select(Post.status, func.count(Post.id)).group_by(Post.status))
    by_status = dict(status_result.all())
    # By language
    lang_result = await db.execute(select(Post.language, func.count(Post.id)).group_by(Post.language))
    by_language = dict(lang_result.all())
    # Recent
    recent_result = await db.execute(select(Post).order_by(Post.created_at.desc()).limit(10))
    recent_posts = list(recent_result.scalars().all())
    return {"total_posts": total, "by_status": by_status, "by_language": by_language, "recent_posts": recent_posts}
