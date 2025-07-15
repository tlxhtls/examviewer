from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

import crud
import models
import database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
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

@app.get("/api/search")
def search_records(
    q: str,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "file_creation_date",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    # 기본적인 검색 로직 (향후 개선 필요)
    query = db.query(models.MedicalRecord).filter(
        (models.MedicalRecord.patient_name.contains(q)) |
        (models.MedicalRecord.patient_id.contains(q))
    )

    # 정렬
    if hasattr(models.MedicalRecord, sort_by):
        column = getattr(models.MedicalRecord, sort_by)
        if sort_order == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    total = query.count()
    results = query.offset(offset).limit(limit).all()

    return {"total": total, "results": results}

# 여기에 /api/file, /api/thumbnail 엔드포인트를 추가할 예정입니다.
