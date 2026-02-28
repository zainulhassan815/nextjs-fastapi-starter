from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DetectionMethod(Base):
    __tablename__ = "detection_methods"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    stage: Mapped[int] = mapped_column(Integer, nullable=False)  # 2 or 3
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 1.0 = full strength, 0.1 = minimum
    decay_factor: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
