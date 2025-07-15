import re

PATTERNS = [
    r"(?P<name>[가-힣]+)_(?P<id>\d+)_.*",           # 홍길동_1234567_검사결과.pdf
    r"(?P<id>\d+)_(?P<name>[가-힣]+)_.*",           # 1234567_홍길동_MRI.docx
    r"(?P<name>[가-힣]+)\s+(?P<id>\d+).*",          # 홍길동 1234567 초음파.pdf
    r"(?P<id>\d+)\s+(?P<name>[가-힣]+).*",          # 1234567 홍길동 CT.pdf
    r".*(?P<name>[가-힣]{2,4}).*(?P<id>\d{6,8}).*", # 일반적인 한글이름+숫자ID
]

def parse_file_name(file_name: str):
    for pattern in PATTERNS:
        match = re.search(pattern, file_name)
        if match:
            data = match.groupdict()
            return {
                "patient_name": data.get("name"),
                "patient_id": data.get("id"),
                "parsing_confidence": 0.95 # 예시 값
            }
    return None
