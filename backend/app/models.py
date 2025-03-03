from database import Base
from sqlalchemy import Column, Integer, Float, DateTime, Enum, JSON
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


class Rsi(Base):
    __tablename__ = "rsi"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(
        Enum("day", "week", "hour4", "hour1", name="timeframe_type"),
        index=True,
        nullable=False,
    )
    rsi_values = Column(
        JSON,  # 변경: Float → JSON (리스트 저장)
        nullable=False,
        comment="RSI 값들의 리스트",
    )
    timestamps = Column(
        JSON,  # 추가: 타임스탬프 리스트 저장용
        nullable=False,
        comment="각 RSI 값에 해당하는 타임스탬프 리스트",
    )
    current_rsi = Column(Float, nullable=False, comment="현재 최신 RSI 값")
    last_updated = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
