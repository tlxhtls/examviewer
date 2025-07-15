from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import crud, models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # 간단한 쿼리로 DB 연결 확인
        db.execute('SELECT 1')
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {e}"

    # Watcher 상태는 별도의 IPC나 파일 기반으로 확인해야 함 (향후 구현)
    return {
        "status": "healthy",
        "database": db_status,
        "watcher": "not_implemented_yet"
    }

# 여기에 /api/search, /api/file, /api/thumbnail 엔드포인트를 추가할 예정입니다.