"""
실시간 파일 시스템 감시 스크립트
Watchdog를 사용하여 NAS 파일 시스템의 변경사항을 감지하고 데이터베이스를 업데이트합니다.
"""
import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 로컬 모듈 import (실제 환경에서는 정상 작동)
try:
    from database import get_db_session, init_database
    from models import MedicalRecord
    from utils.file_parser import FileNameParser
except ImportError:
    print("Warning: Could not import local modules. Running in development mode.")


class MedicalFileHandler(FileSystemEventHandler):
    """의료 파일 변경사항을 처리하는 이벤트 핸들러"""
    
    def __init__(self):
        self.parser = FileNameParser()
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """로거 설정"""
        logger = logging.getLogger('watcher')
        logger.setLevel(logging.INFO)
        
        # 로그 핸들러 설정
        handler = logging.FileHandler('logs/watcher.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # 콘솔 출력도 추가
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def on_created(self, event):
        """파일/폴더 생성 이벤트 처리"""
        if event.is_directory:
            self.logger.info(f"새 폴더 생성: {event.src_path}")
            self._process_directory(event.src_path)
        else:
            self.logger.info(f"새 파일 생성: {event.src_path}")
            self._process_file(event.src_path, action="created")
    
    def on_deleted(self, event):
        """파일/폴더 삭제 이벤트 처리"""
        self.logger.info(f"삭제됨: {event.src_path}")
        self._remove_from_database(event.src_path)
    
    def on_moved(self, event):
        """파일/폴더 이동 이벤트 처리"""
        self.logger.info(f"이동: {event.src_path} -> {event.dest_path}")
        self._update_file_path(event.src_path, event.dest_path)
    
    def on_modified(self, event):
        """파일 수정 이벤트 처리 (선택적)"""
        if not event.is_directory:
            self.logger.debug(f"파일 수정: {event.src_path}")
            # 필요에 따라 수정일자 업데이트 로직 추가
    
    def _process_file(self, file_path: str, action: str = "created"):
        """개별 파일 처리"""
        try:
            # 파일명 파싱
            parse_result = self.parser.parse_filename(file_path)
            
            if not parse_result['success']:
                self.logger.warning(
                    f"파일명 파싱 실패: {file_path}"
                )
                return
            
            # 파일 정보 수집
            file_info = self._collect_file_info(file_path)
            file_info.update(parse_result)
            
            # 데이터베이스에 저장
            self._save_to_database(file_info)
            
            self.logger.info(
                f"파일 처리 완료: {parse_result['patient_name']} "
                f"({parse_result['patient_id']}) - {file_path}"
            )
            
        except Exception as e:
            self.logger.error(f"파일 처리 중 오류: {file_path} - {str(e)}")
    
    def _process_directory(self, dir_path: str):
        """이미지 폴더 처리"""
        try:
            # 폴더명에서 환자 정보 추출
            parse_result = self.parser.parse_folder_name(dir_path)
            
            if not parse_result['success']:
                self.logger.warning(f"폴더명 파싱 실패: {dir_path}")
                return
            
            # 폴더 정보 수집
            folder_info = self._collect_file_info(dir_path)
            folder_info.update(parse_result)
            folder_info['file_type'] = 'IMAGE_FOLDER'
            
            # 데이터베이스에 저장
            self._save_to_database(folder_info)
            
            self.logger.info(
                f"폴더 처리 완료: {parse_result['patient_name']} "
                f"({parse_result['patient_id']}) - {dir_path}"
            )
            
        except Exception as e:
            self.logger.error(f"폴더 처리 중 오류: {dir_path} - {str(e)}")
    
    def _collect_file_info(self, file_path: str) -> Dict:
        """파일/폴더의 메타데이터 수집"""
        try:
            stat = os.stat(file_path)
            
            return {
                'file_path': file_path,
                'file_type': self.parser.get_file_type(file_path),
                'file_size': stat.st_size if os.path.isfile(file_path) else None,
                'file_creation_date': datetime.fromtimestamp(stat.st_ctime),
                'file_modified_date': datetime.fromtimestamp(stat.st_mtime),
            }
        except Exception as e:
            self.logger.error(f"파일 정보 수집 실패: {file_path} - {str(e)}")
            return {}
    
    def _save_to_database(self, file_info: Dict):
        """데이터베이스에 파일 정보 저장"""
        try:
            db = get_db_session()
            
            # 중복 확인
            existing = db.query(MedicalRecord).filter(
                MedicalRecord.file_path == file_info['file_path']
            ).first()
            
            if existing:
                self.logger.info(f"이미 존재하는 파일: {file_info['file_path']}")
                return
            
            # 새 레코드 생성
            record = MedicalRecord(
                patient_name=file_info['patient_name'],
                patient_id=file_info['patient_id'],
                file_path=file_info['file_path'],
                file_type=file_info['file_type'],
                file_size=file_info.get('file_size'),
                file_creation_date=file_info.get('file_creation_date'),
                file_modified_date=file_info.get('file_modified_date'),
                parsing_confidence=file_info.get('confidence', 0.0)
            )
            
            db.add(record)
            db.commit()
            
            self.logger.info(f"데이터베이스 저장 완료: ID {record.id}")
            
        except Exception as e:
            self.logger.error(f"데이터베이스 저장 실패: {str(e)}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    def _remove_from_database(self, file_path: str):
        """데이터베이스에서 파일 정보 삭제"""
        try:
            db = get_db_session()
            
            record = db.query(MedicalRecord).filter(
                MedicalRecord.file_path == file_path
            ).first()
            
            if record:
                db.delete(record)
                db.commit()
                self.logger.info(f"데이터베이스에서 삭제: {file_path}")
            
        except Exception as e:
            self.logger.error(f"데이터베이스 삭제 실패: {file_path} - {str(e)}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()
    
    def _update_file_path(self, old_path: str, new_path: str):
        """파일 경로 업데이트"""
        try:
            db = get_db_session()
            
            record = db.query(MedicalRecord).filter(
                MedicalRecord.file_path == old_path
            ).first()
            
            if record:
                record.file_path = new_path
                record.modified_at = datetime.now()
                db.commit()
                self.logger.info(f"경로 업데이트: {old_path} -> {new_path}")
            
        except Exception as e:
            self.logger.error(f"경로 업데이트 실패: {str(e)}")
            if 'db' in locals():
                db.rollback()
        finally:
            if 'db' in locals():
                db.close()


class FileWatcher:
    """파일 시스템 감시 메인 클래스"""
    
    def __init__(self, config_path: str = "../config/nas_paths.json"):
        self.config_path = config_path
        self.observer = Observer()
        self.handler = MedicalFileHandler()
        self.watch_paths = []
        
    def load_config(self):
        """설정 파일에서 감시할 경로들을 로드"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.watch_paths = config.get('nas_paths', [])
                
            print(f"감시 경로 {len(self.watch_paths)}개 로드됨")
            for path in self.watch_paths:
                print(f"  - {path}")
                
        except FileNotFoundError:
            print(f"설정 파일을 찾을 수 없습니다: {self.config_path}")
            print("기본 경로를 사용합니다.")
            self.watch_paths = ["../demodata"]  # 개발용 기본 경로
        except Exception as e:
            print(f"설정 파일 로드 실패: {e}")
            self.watch_paths = ["../demodata"]
    
    def start_watching(self):
        """파일 시스템 감시 시작"""
        self.load_config()
        
        # 각 경로에 대해 감시 설정
        for path in self.watch_paths:
            if os.path.exists(path):
                self.observer.schedule(
                    self.handler, 
                    path, 
                    recursive=True
                )
                print(f"감시 시작: {path}")
            else:
                print(f"경로가 존재하지 않습니다: {path}")
        
        self.observer.start()
        print("파일 시스템 감시가 시작되었습니다.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n감시 중지 중...")
            self.observer.stop()
        
        self.observer.join()
        print("파일 시스템 감시가 종료되었습니다.")
    
    def scan_initial_files(self):
        """초기 파일 스캔 (기존 파일들을 데이터베이스에 추가)"""
        print("초기 파일 스캔을 시작합니다...")
        
        for watch_path in self.watch_paths:
            if os.path.exists(watch_path):
                for root, dirs, files in os.walk(watch_path):
                    # 폴더 처리 (이미지 폴더)
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        self.handler._process_directory(dir_path)
                    
                    # 파일 처리
                    for file_name in files:
                        file_path = os.path.join(root, file_name)
                        self.handler._process_file(file_path, action="scan")
        
        print("초기 파일 스캔이 완료되었습니다.")


def main():
    """메인 함수"""
    print("=== 환자 검사 파일 감시 시스템 ===")
    
    # 데이터베이스 초기화
    try:
        init_database()
    except Exception as e:
        print(f"데이터베이스 초기화 실패: {e}")
        return
    
    # 파일 감시 시작
    watcher = FileWatcher()
    
    # 초기 스캔 여부 선택
    response = input("초기 파일 스캔을 수행하시겠습니까? (y/N): ")
    if response.lower() in ['y', 'yes']:
        watcher.scan_initial_files()
    
    # 실시간 감시 시작
    watcher.start_watching()


if __name__ == "__main__":
    main() 