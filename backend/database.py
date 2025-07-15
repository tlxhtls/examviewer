"""
데이터베이스 연결 및 세션 관리
SQLite 데이터베이스 연결과 SQLAlchemy 세션을 관리합니다.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from models import Base

# 데이터베이스 파일 경로 설정
DATABASE_URL = "sqlite:///./database.sqlite"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database.sqlite")

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite에서 멀티스레드 허용
    echo=False  # SQL 쿼리 로깅 (개발 시 True로 설정 가능)
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """데이터베이스 테이블을 생성합니다."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI의 Dependency Injection을 위한 데이터베이스 세션 제공자
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    일반적인 용도로 데이터베이스 세션을 반환합니다.
    사용 후 반드시 close()를 호출해야 합니다.
    """
    return SessionLocal()


def init_database():
    """
    데이터베이스를 초기화합니다.
    - 테이블 생성
    - 필요한 디렉토리 생성
    """
    # 데이터베이스 디렉토리 생성
    os.makedirs(BASE_DIR, exist_ok=True)
    
    # 캐시 디렉토리 생성
    cache_dir = os.path.join(BASE_DIR, "cache")
    thumbnail_dir = os.path.join(cache_dir, "thumbnails")
    converted_dir = os.path.join(cache_dir, "converted")
    
    os.makedirs(thumbnail_dir, exist_ok=True)
    os.makedirs(converted_dir, exist_ok=True)
    
    # 로그 디렉토리 생성
    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # 테이블 생성
    create_tables()
    print(f"데이터베이스가 초기화되었습니다: {DATABASE_PATH}")


def check_database_connection() -> bool:
    """데이터베이스 연결 상태를 확인합니다."""
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")
        return False


if __name__ == "__main__":
    # 직접 실행 시 데이터베이스 초기화
    init_database()
    if check_database_connection():
        print("데이터베이스 연결 성공!")
    else:
        print("데이터베이스 연결 실패!") 