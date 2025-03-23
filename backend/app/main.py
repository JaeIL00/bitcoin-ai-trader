from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from ws_connection_manager import WsConnectionManager
from schemas import (
    LogResponse,
    MacdRequest,
    MacdResponse,
    MovingAverageRequest,
    MovingAverageResponse,
    RsiRequest,
    RsiResponse,
    TimeFrameType,
)
from database import get_db, engine, Base
from models import LatestLog, Macd, MovingAverage, Rsi
from typing import List, Dict, Any, Optional


import traceback
import logging

logger = logging.getLogger(__name__)


class ContentInput(BaseModel):
    content: str


# 애플리케이션 객체 생성 전에 테이블 생성 로직을 추가합니다
Base.metadata.create_all(bind=engine)  # 여기서 테이블을 생성합니다!

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://219.250.32.135:3000",
        "http://localhost:3000",
    ],  # 실제 운영 환경에서는 구체적인 출처 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = WsConnectionManager()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse(url="/docs", status_code=303)


@app.get("/api/moving-averages/{type}", response_model=MovingAverageResponse)
async def get_moving_average_by_type(
    type: TimeFrameType, db: Session = Depends(get_db)
):
    """
    이동평균 데이터를 조회합니다.
    type 파라미터를 사용하여 특정 타임프레임의 데이터만 필터링할 수 있습니다.
    """
    try:
        result = (
            db.query(MovingAverage)
            .filter(MovingAverage.type == type)
            .order_by(MovingAverage.last_updated.desc())
            .first()
        )

        # 결과가 없으면 빈 리스트 반환
        if not result:
            raise HTTPException(
                status_code=404, detail=f"ma {type} 타입의 데이터를 찾을 수 없습니다."
            )

        return result
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"ma {type} 데이터 조회 실패: {str(e)}"
        )


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
        raise HTTPException(
            status_code=500, detail=f"ma {type} 데이터 저장 실패: {str(e)}"
        )


@app.put("/api/moving-averages/{type}")
async def update_moving_average_by_type(
    type: TimeFrameType, body: MovingAverageRequest, db: Session = Depends(get_db)
):
    """
    특정 타입의 이동평균 데이터를 업데이트합니다.
    URL 경로의 type과 일치하는 기존 데이터를 요청 본문의 데이터로 대체합니다.
    """
    try:
        # URL 경로의 type과 요청 본문의 type이 일치하는지 확인
        if type != body.type:
            raise HTTPException(
                status_code=400,
                detail=f"ma 경로의 type:{type}과 요청 본문의 type:{body.type}이 일치해야 합니다.",
            )

        # 동일한 type의 기존 데이터 찾기
        existing_records = (
            db.query(MovingAverage).filter(MovingAverage.type == type).all()
        )

        # 트랜잭션 시작
        db.begin_nested()  # savepoint 생성

        # 기존 레코드가 있으면 모두 삭제
        if existing_records:
            for record in existing_records:
                db.delete(record)

        # 새 데이터 생성 및 저장
        new_record = MovingAverage(
            type=type,
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

        db.add(new_record)
        db.commit()

        # 처리 결과 반환
        return {
            "success": True,
        }

    except Exception as e:
        # 오류 발생 시 롤백
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"ma {type} 데이터 업데이트 실패: {str(e)}"
        )


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
        raise HTTPException(
            status_code=500, detail=f"rsi {body.type} 데이터 저장 실패: {str(e)}"
        )


@app.put("/api/rsi/{type}")
async def update_rsi_by_type(
    type: TimeFrameType, body: RsiRequest, db: Session = Depends(get_db)
):
    try:
        if type != body.type:
            raise HTTPException(
                status_code=400,
                detail="경로의 type과 요청 본문의 type이 일치해야 합니다.",
            )

        # 동일한 type의 기존 데이터 찾기
        existing_records = db.query(Rsi).filter(Rsi.type == type).all()

        db.begin_nested()  # savepoint 생성

        # 기존 레코드가 있으면 모두 삭제
        if existing_records:
            for record in existing_records:
                db.delete(record)

        # 트랜잭션 시작

        timestamps_json = [ts.isoformat() for ts in body.timestamps]
        # 입력 데이터를 DB 모델로 변환
        new_record = Rsi(
            type=body.type,
            rsi_values=body.rsi_values,
            timestamps=timestamps_json,
            current_rsi=body.current_rsi,
            last_updated=body.last_updated,
        )

        # DB에 저장
        db.add(new_record)
        db.commit()

        return {"success": True}
    except Exception as e:
        db.rollback()
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"rsi {type} 데이터 업데이트 실패: {str(e)}"
        )


@app.get("/api/rsi/{type}", response_model=RsiResponse)
async def get_rsi_by_type(type: TimeFrameType, db: Session = Depends(get_db)):
    try:
        result = (
            db.query(Rsi)
            .filter(Rsi.type == type)
            .order_by(Rsi.last_updated.desc())
            .first()
        )
        # 결과가 없으면 빈 리스트 반환
        if not result:
            raise HTTPException(
                status_code=404, detail=f"rsi {type} 타입의 데이터를 찾을 수 없습니다."
            )

        return result
    except Exception as e:
        db.rollback()
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"rsi {type} 데이터 조회 실패: {str(e)}"
        )


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
            last_updated=body.last_updated,
        )

        # DB에 저장
        db.add(db_item)
        db.commit()

        return {"success": True}
    except Exception as e:
        db.rollback()
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"madc {body.type} 데이터 저장 실패: {str(e)}"
        )


@app.get("/api/macd/{type}", response_model=MacdResponse)
async def get_macd_by_type(type: TimeFrameType, db: Session = Depends(get_db)):
    """
    이동평균 데이터를 조회합니다.
    type 파라미터를 사용하여 특정 타임프레임의 데이터만 필터링할 수 있습니다.
    """
    try:
        result = (
            db.query(Macd)
            .filter(Macd.type == type)
            .order_by(Macd.last_updated.desc())
            .first()
        )

        # 결과가 없으면 빈 리스트 반환
        if not result:
            raise HTTPException(
                status_code=404, detail=f"Macd {type} 타입의 데이터를 찾을 수 없습니다."
            )

        return result
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Macd {type} 데이터 조회 실패: {str(e)}"
        )


@app.put("/api/macd/{type}")
async def update_macd_by_type(
    type: TimeFrameType, body: MacdRequest, db: Session = Depends(get_db)
):
    """
    특정 타입의 이동평균 데이터를 업데이트합니다.
    URL 경로의 type과 일치하는 기존 데이터를 요청 본문의 데이터로 대체합니다.
    """
    try:
        # URL 경로의 type과 요청 본문의 type이 일치하는지 확인
        if type != body.type:
            raise HTTPException(
                status_code=400,
                detail=f"Macd 경로의 type:{type}과 요청 본문의 type:{body.type}이 일치해야 합니다.",
            )

        # 동일한 type의 기존 데이터 찾기
        existing_records = db.query(Macd).filter(Macd.type == type).all()

        # 트랜잭션 시작
        db.begin_nested()  # savepoint 생성

        # 기존 레코드가 있으면 모두 삭제
        if existing_records:
            for record in existing_records:
                db.delete(record)

        # 새 데이터 생성 및 저장
        dates_json = [date.isoformat() for date in body.dates]
        new_record = Macd(
            type=body.type,
            dates=dates_json,
            macd_line=body.macd_line,
            signal_line=body.signal_line,
            histogram=body.histogram,
            last_updated=body.last_updated,
        )

        db.add(new_record)
        db.commit()

        # 처리 결과 반환
        return {"success": True}

    except Exception as e:
        # 오류 발생 시 롤백
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Macd {type} 데이터 업데이트 실패: {str(e)}"
        )


@app.get("/api/logs", response_model=List[LogResponse])
def get_all_latest_logs(db: Session = Depends(get_db)):
    logs = db.query(LatestLog).order_by(LatestLog.timestamp.asc()).all()
    return logs


@app.post("/api/logs")
async def receive_logs(log: Dict, db: Session = Depends(get_db)):
    existing_log = db.query(LatestLog).filter(LatestLog.module == log["module"]).first()

    if existing_log:
        # 기존 로그 업데이트
        existing_log.message = log["message"]
        existing_log.timestamp = log["timestamp"]
        db.commit()
        db.refresh(existing_log)
        log_obj = existing_log
    else:
        # 새 로그 생성
        log_obj = LatestLog(
            module=log["module"], message=log["message"], timestamp=log["timestamp"]
        )
        db.add(log_obj)
        db.commit()
        db.refresh(log_obj)

    # 로그 수신 후 WebSocket으로 브로드캐스트
    await manager.broadcast(log)
    return {"success": True}


@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    # 연결 수락
    await manager.connect(websocket)

    try:
        # 클라이언트와의 연결 유지
        while True:
            # 클라이언트로부터 메시지 기다리기 (필요한 경우)
            # 여기서는 단순히 연결 유지만을 위한 루프
            data = await websocket.receive_text()
            # 클라이언트로부터 메시지를 받아 처리하려면 여기에 코드 추가

    except Exception as e:
        # 기타 예외 처리
        manager.disconnect(websocket)
        print(f"WebSocket 오류: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
