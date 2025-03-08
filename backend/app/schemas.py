from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import List, Dict, Any, Optional


class TimeFrameType(str, Enum):
    DAY = "day"
    WEEK = "week"
    HOUR4 = "hour4"
    HOUR1 = "hour1"


class MovingAverageResponse(BaseModel):
    id: int
    type: TimeFrameType
    ma: float
    ma_3: Optional[float] = None
    ma_7: Optional[float] = None
    ma_10: Optional[float] = None
    ma_12: Optional[float] = None
    ma_14: Optional[float] = None
    ma_24: Optional[float] = None
    ma_25: Optional[float] = None
    ma_26: Optional[float] = None
    ma_30: Optional[float] = None
    ma_36: Optional[float] = None
    ma_45: Optional[float] = None
    ma_48: Optional[float] = None
    ma_50: Optional[float] = None
    ma_52: Optional[float] = None
    ma_60: Optional[float] = None
    ma_90: Optional[float] = None
    ma_100: Optional[float] = None
    ma_200: Optional[float] = None
    macd_short_period: int
    macd_long_period: int
    signal_period: int
    ma_values: Dict[str, List[Dict[str, Any]]]
    last_updated: datetime
    created_at: datetime

    class Config:
        orm_mode = True  # ORM 모델을 Pydantic 모델로 변환하기 위한 설정


class MovingAverageRequest(BaseModel):
    type: TimeFrameType = Field(..., description="타임프레임 (day, week, hour4, hour1)")

    # 기존 필드 (호환성 유지)
    ma: float = Field(..., description="기본 이동평균값")

    # 추가 이동평균 필드
    ma_3: Optional[float] = Field(None, description="3일/시간 이동평균")
    ma_7: Optional[float] = Field(None, description="7일/시간 이동평균")
    ma_10: Optional[float] = Field(None, description="10일/시간 이동평균")
    ma_12: Optional[float] = Field(None, description="12일/시간 이동평균")
    ma_14: Optional[float] = Field(None, description="14일/시간 이동평균")
    ma_24: Optional[float] = Field(None, description="24일/시간 이동평균")
    ma_25: Optional[float] = Field(None, description="25일/시간 이동평균")
    ma_26: Optional[float] = Field(None, description="26일/시간 이동평균")
    ma_30: Optional[float] = Field(None, description="30일/시간 이동평균")
    ma_36: Optional[float] = Field(None, description="36일/시간 이동평균")
    ma_45: Optional[float] = Field(None, description="45일/시간 이동평균")
    ma_48: Optional[float] = Field(None, description="48일/시간 이동평균")
    ma_50: Optional[float] = Field(None, description="50일/시간 이동평균")
    ma_52: Optional[float] = Field(None, description="52일/시간 이동평균")
    ma_60: Optional[float] = Field(None, description="60일/시간 이동평균")
    ma_90: Optional[float] = Field(None, description="90일/시간 이동평균")
    ma_100: Optional[float] = Field(None, description="100일/시간 이동평균")
    ma_200: Optional[float] = Field(None, description="200일/시간 이동평균")

    # MACD 관련 필드
    macd_short_period: int = Field(..., description="MACD 단기 이동평균 기간")
    macd_long_period: int = Field(..., description="MACD 장기 이동평균 기간")
    signal_period: int = Field(..., description="시그널 라인 계산 기간")

    # 시계열 데이터를 위한 필드
    ma_values: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="다양한 기간의 이동평균 시계열 데이터"
    )

    last_updated: datetime = Field(..., description="마지막 업데이트 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "hour4",
                "ma": 143623561.11,
                "ma_7": 146615714.29,
                "ma_12": 145969250.0,
                "ma_26": 125158000.0,
                "macd_short_period": 12,
                "macd_long_period": 26,
                "signal_period": 9,
                "ma_values": {
                    "ma_12": [
                        {
                            "timestamp": "2025-02-24T00:00:00",
                            "value": 146811000.0,
                            "price": 142500000.0,
                        },
                        {
                            "timestamp": "2025-03-03T00:00:00",
                            "value": 145969250.0,
                            "price": 139142000.0,
                        },
                    ]
                },
                "last_updated": "2025-03-03T05:38:35.158165+00:00",
            }
        }


class RsiRequest(BaseModel):
    type: TimeFrameType = Field(..., description="타임프레임 (day, week, hour4, hour1)")
    rsi_values: List[float] = Field(..., description="RSI 값들")
    timestamps: List[datetime] = Field(..., description="rsi 해당하는 타임스탬프")
    current_rsi: float = Field(..., description="현재 가장 최근 RSI")
    last_updated: datetime = Field(..., description="마지막 rsi 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "hour4",
                "rsi_values": [42.5, 45.8, 51.2, 61.11],
                "timestamps": [
                    "2025-03-01T00:00:00+00:00",
                    "2025-03-01T04:00:00+00:00",
                    "2025-03-02T08:00:00+00:00",
                    "2025-03-02T12:00:00+00:00",
                ],
                "current_rsi": 61.11,
                "last_updated": "2025-03-02T12:39:44.831594+00:00",
            }
        }


class MacdRequest(BaseModel):
    type: TimeFrameType = Field(..., description="타임프레임 (day, week, hour4, hour1)")
    dates: List[datetime] = Field(..., description="각 값에 해당하는 타임스탬프 리스트")
    macd_line: List[float] = Field(..., description="MACD 라인 값들의 리스트")
    signal_line: List[float] = Field(..., description="시그널 라인 값들의 리스트")
    histogram: List[float] = Field(..., description="히스토그램 값들의 리스트")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "hour4",
                "dates": [
                    "2025-02-28 00:00:00",
                    "2025-03-01 00:00:00",
                    "2025-03-02 00:00:00",
                    "2025-03-03 00:00:00",
                    "2025-03-04 00:00:00",
                    "2025-03-05 00:00:00",
                ],
                "macd_line": [
                    -4629910.25,
                    -4513974.36,
                ],
                "signal_line": [
                    -4629910.25,
                    -4513974.36,
                ],
                "histogram": [
                    -4629910.25,
                    -4513974.36,
                ],
            }
        }
