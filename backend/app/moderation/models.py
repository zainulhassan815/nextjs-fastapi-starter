from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class ModerationResult(Base):
    __tablename__ = "moderation_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False, index=True)
    stage: Mapped[int] = mapped_column(Integer, nullable=False)  # 1, 2, or 3
    method_name: Mapped[str | None] = mapped_column(String(100), nullable=True)  # detection method used (stage 2/3)
    verdict: Mapped[str] = mapped_column(String(20), nullable=False)  # safe, harmful, uncertain, escalate
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
