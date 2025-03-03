from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


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
