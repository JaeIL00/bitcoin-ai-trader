from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import (
    MacdRequest,
    MovingAverageRequest,
    MovingAverageResponse,
    RsiRequest,
    TimeFrameType,
)
from database import get_db, engine, Base
from models import Macd, MovingAverage, Rsi
from typing import List, Dict, Any, Optional


import traceback
import logging

logger = logging.getLogger(__name__)


class ContentInput(BaseModel):
    content: str


# 애플리케이션 객체 생성 전에 테이블 생성 로직을 추가합니다
Base.metadata.create_all(bind=engine)  # 여기서 테이블을 생성합니다!

app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse(url="/docs", status_code=303)


@app.get("/api/moving-averages", response_model=List[MovingAverageResponse])
async def get_moving_averages(
    type: Optional[TimeFrameType], db: Session = Depends(get_db)
):
    """
    이동평균 데이터를 조회합니다.
    type 파라미터를 사용하여 특정 타임프레임의 데이터만 필터링할 수 있습니다.
    """
    try:
        # 쿼리 작성
        query = db.query(MovingAverage)

        # 타입 필터 적용
        if type:
            query = query.filter(MovingAverage.type == type)

        # 최신 데이터 우선 정렬
        query = query.order_by(MovingAverage.last_updated.desc())

        # 데이터 조회
        results = query.all()

        # 결과가 없으면 빈 리스트 반환
        if not results:
            return []

        return results
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")


@app.post("/api/moving-averages")
async def create_moving_average(
    body: MovingAverageRequest, db: Session = Depends(get_db)
):
    try:
        # 입력 데이터를 DB 모델로 변환
        db_item = MovingAverage(
            type=body.type,
            ma=body.ma,
            ma_3=body.ma_3,
            ma_7=body.ma_7,
            ma_10=body.ma_10,
            ma_12=body.ma_12,
            ma_14=body.ma_14,
            ma_24=body.ma_24,
            ma_25=body.ma_25,
            ma_26=body.ma_26,
            ma_30=body.ma_30,
            ma_36=body.ma_36,
            ma_45=body.ma_45,
            ma_48=body.ma_48,
            ma_50=body.ma_50,
            ma_52=body.ma_52,
            ma_60=body.ma_60,
            ma_90=body.ma_90,
            ma_100=body.ma_100,
            ma_200=body.ma_200,
            macd_short_period=body.macd_short_period,
            macd_long_period=body.macd_long_period,
            signal_period=body.signal_period,
            ma_values=body.ma_values,
            last_updated=body.last_updated,
        )

        # DB에 저장
        db.add(db_item)
        db.commit()

        return {"success": True}
    except Exception as e:
        db.rollback()
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"데이터 저장 실패: {str(e)}")


@app.post("/api/rsi")
async def create_rsi(body: RsiRequest, db: Session = Depends(get_db)):
    try:
        timestamps_json = [ts.isoformat() for ts in body.timestamps]
        # 입력 데이터를 DB 모델로 변환
        db_item = Rsi(
            type=body.type,
            rsi_values=body.rsi_values,
            timestamps=timestamps_json,
            current_rsi=body.current_rsi,
            last_updated=body.last_updated,
        )

        # DB에 저장
        db.add(db_item)
        db.commit()

        return {"success": True}
    except Exception as e:
        db.rollback()
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"데이터 저장 실패: {str(e)}")


@app.post("/api/macd")
async def create_macd(body: MacdRequest, db: Session = Depends(get_db)):
    try:
        dates_json = [date.isoformat() for date in body.dates]
        db_item = Macd(
            type=body.type,
            dates=dates_json,
            macd_line=body.macd_line,
            signal_line=body.signal_line,
            histogram=body.histogram,
        )

        # DB에 저장
        db.add(db_item)
        db.commit()

        return {"success": True}
    except Exception as e:
        db.rollback()
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"데이터 저장 실패: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
