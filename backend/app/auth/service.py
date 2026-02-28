from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import hash_password, verify_password
from app.users.models import User
from app.users.service import get_user_by_email


async def create_user(db: AsyncSession, email: str, password: str, full_name: str | None = None) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
