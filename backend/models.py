"""
데이터베이스 모델 정의
SQLAlchemy를 사용하여 medical_records 테이블을 정의합니다.
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class MedicalRecord(Base):
    """환자 검사 기록을 저장하는 테이블"""
    
    __tablename__ = "medical_records"
    
    # 기본 정보
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_name = Column(String(50), nullable=False, 
                         comment="환자명 (추출된 정보)")
    patient_id = Column(String(20), nullable=False, 
                       comment="등록번호 (추출된 정보)")
    
    # 파일 정보
    file_path = Column(Text, nullable=False, unique=True, 
                      comment="파일의 전체 UNC 경로")
    file_type = Column(String(20), nullable=False, 
                      comment="파일 종류 (PDF, DOCX, IMAGE_FOLDER)")
    file_size = Column(Integer, nullable=True, comment="파일 크기 (바이트)")
    
    # 날짜 정보
    file_creation_date = Column(DateTime, nullable=True, 
                               comment="파일 시스템상의 생성일")
    file_modified_date = Column(DateTime, nullable=True, 
                               comment="파일 시스템상의 수정일")
    
    # 캐시 및 메타데이터
    thumbnail_path = Column(String(255), nullable=True, 
                           comment="썸네일 캐시 경로")
    parsing_confidence = Column(Float, nullable=True, default=0.0, 
                               comment="파일명 파싱 신뢰도 (0-1)")
    
    # 레코드 관리
    created_at = Column(DateTime, nullable=False, default=func.now(), 
                       comment="레코드 생성 시각")
    modified_at = Column(DateTime, nullable=False, default=func.now(), 
                        onupdate=func.now(), comment="레코드 수정 시각")
    
    def __repr__(self):
        return f"<MedicalRecord(id={self.id}, patient_name='{self.patient_name}', patient_id='{self.patient_id}', file_type='{self.file_type}')>"
    
    def to_dict(self):
        """모델을 딕셔너리로 변환"""
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'patient_id': self.patient_id,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'file_creation_date': self.file_creation_date.isoformat() if self.file_creation_date else None,
            'file_modified_date': self.file_modified_date.isoformat() if self.file_modified_date else None,
            'thumbnail_path': self.thumbnail_path,
            'parsing_confidence': self.parsing_confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
        }


# 인덱스 정의 (PRD에 명시된 성능 최적화를 위한 인덱스)
Index('idx_patient_name', MedicalRecord.patient_name)
Index('idx_patient_id', MedicalRecord.patient_id)
Index('idx_file_creation_date', MedicalRecord.file_creation_date)
Index('idx_composite_search', MedicalRecord.patient_name, MedicalRecord.patient_id, MedicalRecord.file_creation_date)
Index('idx_file_type', MedicalRecord.file_type) 