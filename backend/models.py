import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    patient_id = Column(String, index=True)
    file_path = Column(String, unique=True, index=True)
    file_type = Column(String)
    file_size = Column(Integer)
    file_creation_date = Column(DateTime, index=True)
    file_modified_date = Column(DateTime)
    thumbnail_path = Column(String, nullable=True)
    parsing_confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_db_and_tables()
