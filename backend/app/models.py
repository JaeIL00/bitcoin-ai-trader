from database import Base
from sqlalchemy import Column, Integer, Float, DateTime, Enum
from sqlalchemy.sql import func


class MovingAverage(Base):
    __tablename__ = "moving_averages"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(
        Enum("day", "week", "hour4", "hour1", name="timeframe_type"),
        index=True,
        nullable=False,
    )
    oldest_price = Column(
        Float,
        nullable=False,
    )
    ma = Column(
        Float,
        nullable=False,
    )
    last_updated = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
