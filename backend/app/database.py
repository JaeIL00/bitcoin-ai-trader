from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,  # SQL 쿼리 로깅 활성화 (개발 환경에서 유용)
    pool_pre_ping=True,  # 연결 확인 기능 추가
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 객체 생성
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.close()
