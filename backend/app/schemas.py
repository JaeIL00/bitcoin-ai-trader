from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import List


class TimeFrameType(str, Enum):
    DAY = "day"
    WEEK = "week"
    HOUR4 = "hour4"
    HOUR1 = "hour1"


class MovingAverageRequest(BaseModel):
    type: TimeFrameType = Field(..., description="타임프레임 (day, week, hour4, hour1)")
    oldest_price: float = Field(..., description="최초 가격")
    ma: float = Field(..., description="이동평균값")
    last_updated: datetime = Field(..., description="마지막 업데이트 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "hour4",
                "oldest_price": 156451000.0,
                "ma": 143623561.11,
                "last_updated": "2025-03-02T12:39:44.831594+00:00",
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
