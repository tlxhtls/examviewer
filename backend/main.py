"""
환자 검사 통합 뷰어 백엔드 API
FastAPI를 사용한 메인 애플리케이션
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uvicorn

# 로컬 모듈 import
try:
    from database import get_db, init_database, check_database_connection
    from models import MedicalRecord
    from utils.file_parser import FileNameParser
except ImportError:
    print("Warning: Local modules not found. Running in development mode.")


# FastAPI 앱 생성
app = FastAPI(
    title="환자 검사 통합 뷰어 API",
    description="NAS에 분산된 환자 검사 결과를 통합 검색하는 백엔드 API",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("=== 환자 검사 통합 뷰어 API 시작 ===")
    
    # 데이터베이스 초기화
    try:
        init_database()
        if check_database_connection():
            print("✅ 데이터베이스 연결 성공")
        else:
            print("❌ 데이터베이스 연결 실패")
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")


@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "환자 검사 통합 뷰어 API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """시스템 상태 확인 API"""
    try:
        # 데이터베이스 연결 상태 확인
        db_status = "connected" if check_database_connection() else "disconnected"
        
        # 인덱싱된 파일 수 확인
        total_files = db.query(MedicalRecord).count()
        
        # 캐시 크기 확인 (대략적)
        cache_size = "Unknown"
        try:
            cache_path = "./cache"
            if os.path.exists(cache_path):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(cache_path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        total_size += os.path.getsize(filepath)
                cache_size = f"{total_size // 1024 // 1024}MB"
        except Exception:
            pass
        
        return {
            "status": "healthy",
            "database": db_status,
            "watcher": "running",  # TODO: 실제 watcher 상태 확인
            "cache_size": cache_size,
            "indexed_files": total_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/api/search")
async def search_medical_records(
    q: str = Query(..., description="검색어 (환자명 또는 등록번호)"),
    limit: int = Query(50, description="결과 개수 제한"),
    offset: int = Query(0, description="페이지네이션 오프셋"),
    sort_by: str = Query("file_creation_date", description="정렬 기준"),
    sort_order: str = Query("desc", description="정렬 순서 (asc/desc)"),
    db: Session = Depends(get_db)
):
    """환자명 또는 등록번호로 검사 기록 검색"""
    try:
        # 검색 쿼리 구성
        query = db.query(MedicalRecord)
        
        # 검색어가 숫자면 등록번호로, 한글이면 이름으로 검색
        if q.isdigit():
            query = query.filter(MedicalRecord.patient_id.contains(q))
        else:
            query = query.filter(MedicalRecord.patient_name.contains(q))
        
        # 정렬 적용
        if sort_order.lower() == "desc":
            if sort_by == "file_creation_date":
                query = query.order_by(MedicalRecord.file_creation_date.desc())
            elif sort_by == "patient_name":
                query = query.order_by(MedicalRecord.patient_name.desc())
            elif sort_by == "created_at":
                query = query.order_by(MedicalRecord.created_at.desc())
        else:
            if sort_by == "file_creation_date":
                query = query.order_by(MedicalRecord.file_creation_date.asc())
            elif sort_by == "patient_name":
                query = query.order_by(MedicalRecord.patient_name.asc())
            elif sort_by == "created_at":
                query = query.order_by(MedicalRecord.created_at.asc())
        
        # 전체 개수 확인
        total = query.count()
        
        # 페이지네이션 적용
        results = query.offset(offset).limit(limit).all()
        
        # 결과를 딕셔너리로 변환
        result_list = [record.to_dict() for record in results]
        
        return {
            "total": total,
            "results": result_list,
            "query": q,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/api/file/{record_id}")
async def get_file(record_id: int, db: Session = Depends(get_db)):
    """원본 파일 스트리밍 제공"""
    try:
        # 레코드 조회
        record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
        
        file_path = record.file_path
        
        # 파일 존재 확인
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="파일이 존재하지 않습니다.")
        
        # 파일 타입에 따른 처리
        if record.file_type == "DOCX":
            # TODO: DOCX를 PDF로 변환하여 제공
            # 현재는 원본 파일 제공
            return FileResponse(
                file_path,
                filename=os.path.basename(file_path),
                headers={"Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
            )
        elif record.file_type == "PDF":
            return FileResponse(
                file_path,
                filename=os.path.basename(file_path),
                headers={"Content-Type": "application/pdf"}
            )
        elif record.file_type == "IMAGE_FOLDER":
            # TODO: 이미지 폴더를 PDF로 변환하여 제공
            raise HTTPException(status_code=501, detail="이미지 폴더 처리가 아직 구현되지 않았습니다.")
        else:
            # 기타 파일은 원본 제공
            return FileResponse(file_path, filename=os.path.basename(file_path))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File serving failed: {str(e)}")


@app.get("/api/thumbnail/{record_id}")
async def get_thumbnail(record_id: int, db: Session = Depends(get_db)):
    """썸네일 이미지 제공"""
    try:
        # 레코드 조회
        record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="레코드를 찾을 수 없습니다.")
        
        # 캐시된 썸네일 확인
        if record.thumbnail_path and os.path.exists(record.thumbnail_path):
            return FileResponse(
                record.thumbnail_path,
                headers={"Content-Type": "image/png"}
            )
        
        # 썸네일이 없으면 생성
        # TODO: 파일 타입에 따른 썸네일 생성 로직 구현
        
        # 임시로 기본 썸네일 제공
        default_thumbnail = "./static/default_thumbnail.png"
        if os.path.exists(default_thumbnail):
            return FileResponse(default_thumbnail, headers={"Content-Type": "image/png"})
        
        raise HTTPException(status_code=404, detail="썸네일을 생성할 수 없습니다.")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail generation failed: {str(e)}")


@app.get("/api/records")
async def list_all_records(
    limit: int = Query(100, description="결과 개수 제한"),
    offset: int = Query(0, description="페이지네이션 오프셋"),
    db: Session = Depends(get_db)
):
    """모든 레코드 목록 조회 (개발/테스트용)"""
    try:
        query = db.query(MedicalRecord).order_by(MedicalRecord.created_at.desc())
        total = query.count()
        results = query.offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "results": [record.to_dict() for record in results],
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list records: {str(e)}")


@app.delete("/api/records/{record_id}")
async def delete_record(record_id: int, db: Session = Depends(get_db)):
    """레코드 삭제 (개발/테스트용)"""
    try:
        record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
        
        if not record:
            raise HTTPException(status_code=404, detail="레코드를 찾을 수 없습니다.")
        
        db.delete(record)
        db.commit()
        
        return {"message": f"레코드 {record_id}가 삭제되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete record: {str(e)}")


if __name__ == "__main__":
    # 개발 서버 실행
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
