import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context
from app.config import settings
from app.db import Base
from app.budget.models import CostLog  # noqa: F401 — ensure model is registered
from app.content.models import Post  # noqa: F401 — ensure model is registered
from app.detection.models import DetectionMethod  # noqa: F401 — ensure model is registered
from app.moderation.models import ModerationResult  # noqa: F401 — ensure model is registered
from app.review.models import ReviewItem  # noqa: F401 — ensure model is registered
from app.users.models import User  # noqa: F401 — ensure model is registered

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = create_async_engine(settings.database_url)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
