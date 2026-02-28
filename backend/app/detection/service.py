import random

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.detection.models import DetectionMethod

# Decay constants
DECAY_RATE = 0.02  # Each usage reduces decay factor by this amount
MIN_DECAY = 0.1  # Minimum decay factor (never fully excluded)


async def list_methods(db: AsyncSession, stage: int | None = None) -> list[DetectionMethod]:
    """List all detection methods, optionally filtered by stage."""
    query = select(DetectionMethod).order_by(DetectionMethod.stage, DetectionMethod.name)
    if stage is not None:
        query = query.where(DetectionMethod.stage == stage)
    result = await db.execute(query)
    return list(result.scalars().all())


async def select_method(db: AsyncSession, stage: int) -> DetectionMethod | None:
    """Select a detection method using weighted random based on decay factor."""
    methods = await list_methods(db, stage=stage)
    if not methods:
        return None
    weights = [m.decay_factor for m in methods]
    return random.choices(methods, weights=weights, k=1)[0]


async def record_usage(db: AsyncSession, method_id: int) -> None:
    """Record a usage and apply decay to the method."""
    method = await db.get(DetectionMethod, method_id)
    if not method:
        return
    method.usage_count += 1
    method.decay_factor = max(MIN_DECAY, method.decay_factor - DECAY_RATE)
    await db.commit()


async def reset_all_methods(db: AsyncSession) -> int:
    """Reset all detection methods to full strength. Returns count of methods reset."""
    result = await db.execute(update(DetectionMethod).values(decay_factor=1.0, usage_count=0))
    await db.commit()
    return result.rowcount  # type: ignore[return-value]
