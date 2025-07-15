"""
파일명 파싱 유틸리티
다양한 파일명 패턴에서 환자명과 등록번호를 추출합니다.
"""
import re
import os
from typing import Dict


class FileNameParser:
    """파일명에서 환자명과 등록번호를 추출하는 클래스"""
    
    def __init__(self):
        # PRD에 명시된 파일명 패턴들
        self.patterns = [
            # 패턴 1: 홍길동_1234567_검사결과.pdf
            {
                'pattern': r'(?P<name>[가-힣]{2,5})_(?P<id>\d{6,8})_.*',
                'confidence': 0.95,
                'description': '이름_번호_설명 형식'
            },
            # 패턴 2: 1234567_홍길동_MRI.docx
            {
                'pattern': r'(?P<id>\d{6,8})_(?P<name>[가-힣]{2,5})_.*',
                'confidence': 0.95,
                'description': '번호_이름_설명 형식'
            },
            # 패턴 3: 홍길동 1234567 초음파.pdf
            {
                'pattern': r'(?P<name>[가-힣]{2,5})\s+(?P<id>\d{6,8}).*',
                'confidence': 0.90,
                'description': '이름 번호 설명 형식'
            },
            # 패턴 4: 1234567 홍길동 CT.pdf
            {
                'pattern': r'(?P<id>\d{6,8})\s+(?P<name>[가-힣]{2,5}).*',
                'confidence': 0.90,
                'description': '번호 이름 설명 형식'
            },
            # 패턴 5: 일반적인 한글이름+숫자ID 패턴
            {
                'pattern': r'.*(?P<name>[가-힣]{2,5}).*(?P<id>\d{6,8}).*',
                'confidence': 0.70,
                'description': '이름과 번호가 포함된 일반 형식'
            },
            # 패턴 6: 숫자ID+한글이름 패턴
            {
                'pattern': r'.*(?P<id>\d{6,8}).*(?P<name>[가-힣]{2,5}).*',
                'confidence': 0.70,
                'description': '번호와 이름이 포함된 일반 형식'
            }
        ]
    
    def parse_filename(self, file_path: str) -> Dict[str, any]:
        """
        파일명에서 환자명과 등록번호를 추출합니다.
        
        Args:
            file_path: 파일의 전체 경로
            
        Returns:
            dict: {
                'patient_name': str,
                'patient_id': str,
                'confidence': float,
                'pattern_used': str,
                'success': bool
            }
        """
        filename = os.path.basename(file_path)
        filename_no_ext = os.path.splitext(filename)[0]
        
        result = {
            'patient_name': None,
            'patient_id': None,
            'confidence': 0.0,
            'pattern_used': None,
            'success': False
        }
        
        # 각 패턴을 순서대로 시도
        for pattern_info in self.patterns:
            pattern = pattern_info['pattern']
            match = re.match(pattern, filename_no_ext)
            
            if match:
                try:
                    groups = match.groupdict()
                    if 'name' in groups and 'id' in groups:
                        name = groups['name']
                        patient_id = groups['id']
                        
                        # 유효성 검사
                        if self._validate_extraction(name, patient_id):
                            result.update({
                                'patient_name': name,
                                'patient_id': patient_id,
                                'confidence': pattern_info['confidence'],
                                'pattern_used': pattern_info['description'],
                                'success': True
                            })
                            return result
                except Exception:
                    continue
        
        return result
    
    def _validate_extraction(self, name: str, patient_id: str) -> bool:
        """추출된 이름과 등록번호의 유효성을 검사합니다."""
        # 이름 검사: 2-5자의 한글
        if not name or len(name) < 2 or len(name) > 5:
            return False
        if not re.match(r'^[가-힣]+$', name):
            return False
            
        # 등록번호 검사: 6-8자리 숫자
        if not patient_id or len(patient_id) < 6 or len(patient_id) > 8:
            return False
        if not patient_id.isdigit():
            return False
            
        return True
    
    def parse_folder_name(self, folder_path: str) -> Dict[str, any]:
        """
        폴더명에서 환자명과 등록번호를 추출합니다.
        이미지 폴더의 경우 폴더명에서 정보를 추출합니다.
        """
        return self.parse_filename(folder_path)
    
    def get_file_type(self, file_path: str) -> str:
        """파일 확장자를 기반으로 파일 타입을 결정합니다."""
        if os.path.isdir(file_path):
            # 폴더인 경우 이미지 폴더로 간주
            return "IMAGE_FOLDER"
        
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.pdf':
            return "PDF"
        elif ext in ['.docx', '.doc']:
            return "DOCX"
        elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            return "IMAGE"
        else:
            return "UNKNOWN"


def test_parser():
    """파서 테스트 함수"""
    parser = FileNameParser()
    
    test_files = [
        "홍길동_1234567_검사결과.pdf",
        "1234567_홍길동_MRI.docx", 
        "홍길동 1234567 초음파.pdf",
        "1234567 홍길동 CT.pdf",
        "김민준_7654321_혈액검사.pdf",
        "이서아 7654321 종합검진.pdf",
        "박도현_5555555_MRI.docx"
    ]
    
    print("=== 파일명 파싱 테스트 ===")
    for filename in test_files:
        result = parser.parse_filename(filename)
        print(f"파일명: {filename}")
        print(f"결과: {result}")
        print("-" * 50)


if __name__ == "__main__":
    test_parser() 