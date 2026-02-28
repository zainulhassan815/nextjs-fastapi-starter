"""Seed script — run with: uv run python -m scripts.seed"""
import asyncio

from app.auth.service import create_user
from app.db import async_session_maker
from app.users.service import get_user_by_email


async def seed():
    async with async_session_maker() as db:
        test_user = await get_user_by_email(db, "test@example.com")
        if not test_user:
            await create_user(db, email="test@example.com", password="password123", full_name="Test User")
            print("Created test user: test@example.com / password123")
        else:
            print("Test user already exists")


if __name__ == "__main__":
    asyncio.run(seed())
