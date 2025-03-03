from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import MovingAverageRequest, RsiRequest
from database import get_db, engine, Base
from models import MovingAverage, Rsi


class ContentInput(BaseModel):
    content: str


# 애플리케이션 객체 생성 전에 테이블 생성 로직을 추가합니다
Base.metadata.create_all(bind=engine)  # 여기서 테이블을 생성합니다!

app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse(url="/docs", status_code=303)


@app.post("/api/moving-averages")
async def create_moving_average(
    body: MovingAverageRequest, db: Session = Depends(get_db)
):
    try:
        # 입력 데이터를 DB 모델로 변환
        db_item = MovingAverage(
            type=body.type,
            oldest_price=body.oldest_price,
            ma=body.ma,
            last_updated=body.last_updated,
        )

        # DB에 저장
        db.add(db_item)
        db.commit()

        return {"success": True}
    except Exception as e:
        db.rollback()
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
        raise HTTPException(status_code=500, detail=f"데이터 저장 실패: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
