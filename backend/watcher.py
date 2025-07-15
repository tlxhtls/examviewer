import json
import os
import time
import datetime
from sqlalchemy.orm import Session
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from . import crud, models
from .utils.file_parser import parse_file_name

# 데이터베이스 세션 설정 (실제 앱에서는 FastAPI의 의존성 주입을 통해 관리)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, db_session):
        self.db = db_session

    def process(self, event):
        """이벤트 처리의 핵심 로직"""
        if event.is_directory:
            return

        file_path = event.src_path
        # 지원하는 파일 확장자 (나중에 config로 옮길 수 있음)
        if not file_path.lower().endswith(('.pdf', '.docx', '.jpg', '.png')):
            return

        if event.event_type == 'created':
            self.on_created(file_path)
        elif event.event_type == 'deleted':
            self.on_deleted(file_path)
        elif event.event_type == 'moved':
            self.on_moved(event.src_path, event.dest_path)

    def on_created(self, file_path):
        print(f"File created: {file_path}")
        parsed_data = parse_file_name(os.path.basename(file_path))
        if not parsed_data:
            print(f"Could not parse file name: {file_path}")
            return

        stat = os.stat(file_path)
        record_data = {
            "patient_name": parsed_data['patient_name'],
            "patient_id": parsed_data['patient_id'],
            "file_path": file_path,
            "file_type": os.path.splitext(file_path)[1].upper().replace('.', ''),
            "file_size": stat.st_size,
            "file_creation_date": datetime.datetime.fromtimestamp(stat.st_ctime),
            "file_modified_date": datetime.datetime.fromtimestamp(stat.st_mtime),
            "parsing_confidence": parsed_data['parsing_confidence']
        }
        crud.create_record(self.db, record_data)
        print(f"Record created for: {file_path}")

    def on_deleted(self, file_path):
        print(f"File deleted: {file_path}")
        db_record = crud.get_record_by_path(self.db, file_path)
        if db_record:
            crud.delete_record(self.db, db_record)
            print(f"Record deleted for: {file_path}")

    def on_moved(self, src_path, dest_path):
        print(f"File moved from {src_path} to {dest_path}")
        db_record = crud.get_record_by_path(self.db, src_path)
        if db_record:
            update_data = {"file_path": dest_path}
            crud.update_record(self.db, db_record, update_data)
            print(f"Record updated for: {dest_path}")

    def on_modified(self, event):
        if not event.is_directory:
            self.process(event)

def initial_scan(db: Session, paths: list):
    print("Starting initial scan...")
    for path in paths:
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if not crud.get_record_by_path(db, file_path):
                    handler = FileChangeHandler(db)
                    # on_created 로직 재활용
                    handler.on_created(file_path)
    print("Initial scan finished.")

def start_watching(paths: list):
    db = SessionLocal()
    # 초기 스캔 실행
    initial_scan(db, paths)

    event_handler = FileChangeHandler(db)
    observer = Observer()
    for path in paths:
        observer.schedule(event_handler, path, recursive=True)
        print(f"Watching directory: {path}")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    db.close()

if __name__ == "__main__":
    with open("../config/nas_paths.json", 'r') as f:
        config = json.load(f)
    
    # 상대 경로를 절대 경로로 변환
    # 이 스크립트는 backend/ 에서 실행되므로, ../ 를 기준으로 경로를 재계산해야 합니다.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    abs_paths = [os.path.join(project_root, os.path.normpath(p)) if not os.path.isabs(p) else p for p in config['paths']]

    start_watching(abs_paths)
