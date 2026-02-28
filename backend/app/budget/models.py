from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class CostLog(Base):
    __tablename__ = "cost_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    stage: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, default="claude-haiku-4-5-20241022")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
