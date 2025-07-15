from sqlalchemy.orm import Session
from . import models

def get_record_by_path(db: Session, file_path: str):
    return db.query(models.MedicalRecord).filter(models.MedicalRecord.file_path == file_path).first()

def create_record(db: Session, record_data: dict):
    db_record = models.MedicalRecord(**record_data)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def update_record(db: Session, db_record, update_data: dict):
    for key, value in update_data.items():
        setattr(db_record, key, value)
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_record(db: Session, db_record):
    db.delete(db_record)
    db.commit()
