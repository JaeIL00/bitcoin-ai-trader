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

    # 기존 열 유지 (호환성)
    ma = Column(Float, nullable=False)

    # 추가 이동평균 값들
    ma_3 = Column(Float, nullable=True)
    ma_7 = Column(Float, nullable=True)
    ma_10 = Column(Float, nullable=True)
    ma_12 = Column(Float, nullable=True)
    ma_14 = Column(Float, nullable=True)
    ma_24 = Column(Float, nullable=True)
    ma_25 = Column(Float, nullable=True)
    ma_26 = Column(Float, nullable=True)
    ma_30 = Column(Float, nullable=True)
    ma_36 = Column(Float, nullable=True)
    ma_45 = Column(Float, nullable=True)
    ma_48 = Column(Float, nullable=True)
    ma_50 = Column(Float, nullable=True)
    ma_52 = Column(Float, nullable=True)
    ma_60 = Column(Float, nullable=True)
    ma_90 = Column(Float, nullable=True)
    ma_100 = Column(Float, nullable=True)
    ma_200 = Column(Float, nullable=True)

    # MACD 관련 필드
    macd_short_period = Column(Integer, nullable=False)
    macd_long_period = Column(Integer, nullable=False)
    signal_period = Column(Integer, nullable=False)

    # 시계열 데이터를 JSON으로 저장
    ma_values = Column(JSON, nullable=False)

    # 기존 시간 필드
    last_updated = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
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


class Macd(Base):
    __tablename__ = "macd"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(
        Enum("day", "week", "hour4", "hour1", name="timeframe_type"),
        index=True,
        nullable=False,
    )
    dates = Column(
        JSON,
        nullable=False,
        comment="각 값에 해당하는 타임스탬프 리스트",
    )
    macd_line = Column(
        JSON,
        nullable=False,
        comment="MACD 라인 값들의 리스트",
    )
    signal_line = Column(
        JSON,
        nullable=False,
        comment="시그널 라인 값들의 리스트",
    )
    histogram = Column(
        JSON,
        nullable=False,
        comment="히스토그램 값들의 리스트",
    )
