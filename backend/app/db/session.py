from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

# Async — FastAPI
async_engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Sync — Celery
sync_engine = create_engine(settings.sync_database_url, echo=settings.debug)
sync_session_maker = sessionmaker(sync_engine, class_=Session, expire_on_commit=False)
