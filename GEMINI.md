# GEMINI.md - AI 협업 가이드

이 문서는 AI 개발자가 "환자 검사 통합 뷰어" 프로젝트의 기술적 구조와 핵심 로직을 빠르게 파악하고 기여할 수 있도록 돕기 위해 작성되었습니다.

## 1. 프로젝트 개요

- **목표**: 여러 NAS에 분산된 환자 검사 파일(PDF, DOCX, 이미지 등)을 단일 데스크톱 앱에서 신속하게 검색하고 동시에 미리 볼 수 있는 솔루션 개발.
- **핵심**: Electron + Next.js 프론트엔드와 Python FastAPI 백엔드를 결합하여 의료진의 정보 접근성과 업무 효율성을 극대화.

## 2. 기술 스택 (Tech Stack)

- **저장소**: Monorepo (npm/yarn Workspaces)
- **프론트엔드**: Electron, Next.js (React), TypeScript, Tailwind CSS
- **백엔드**: Python 3.9+, FastAPI, UV (의존성 관리)
- **데이터베이스**: SQLite
- **핵심 라이브러리**:
  - **Backend**: `watchdog` (파일 감시), `docx2pdf` (DOCX 변환), `PyMuPDF` (PDF 썸네일), `Pillow` & `reportlab` (이미지→PDF), `SQLAlchemy` (ORM)
  - **Frontend**: `react-pdf` (PDF 렌더링), `axios` (API 통신)
- **배포**: `electron-builder` (.exe 패키징), `NSSM` (백엔드 서비스화)

## 3. 프로젝트 구조

```
/
├── 📁 backend/                # FastAPI 백엔드
│   ├── main.py               # API 서버 실행
│   ├── watcher.py              # 파일 시스템 감시 독립 프로세스
│   ├── crud.py, models.py    # DB 로직 및 스키마
│   ├── utils/                  # 파일 파싱, 변환 등 유틸리티
│   └── pyproject.toml          # Python 의존성
├── 📁 frontend/               # Next.js + Electron 프론트엔드
│   ├── main.js                 # Electron 메인 프로세스
│   ├── pages/                  # Next.js 페이지
│   ├── components/             # React 컴포넌트
│   └── package.json            # Node.js 의존성
├── 📁 config/                 # 핵심 설정 파일
│   ├── nas_paths.json          # 감시할 NAS 경로
│   └── app_settings.json       # 앱 설정
├── 📁 docs/                   # 프로젝트 문서
├── package.json              # 최상위 Monorepo 관리 스크립트
└── README.md
```

## 4. 핵심 백엔드 로직 (`backend/`)

- **실시간 파일 인덱싱 (`watcher.py`)**:
  - `watchdog` 기반의 독립 스크립트로, Windows 서비스로 실행되도록 설계.
  - `config/nas_paths.json`에 정의된 모든 경로를 실시간으로 감시.
  - 파일명에서 정규식을 이용해 `환자명`과 `등록번호`를 추출.
  - 추출된 메타데이터(파일 경로, 환자 정보, 생성일 등)를 SQLite DB에 저장.
  - 파일 생성/삭제/이동 이벤트에 따라 DB를 자동으로 업데이트.

- **핵심 API (`main.py`)**:
  - `GET /api/search`: 환자 정보로 파일 메타데이터 목록을 검색.
  - `GET /api/thumbnail/{id}`: 문서의 첫 페이지를 경량 PNG 썸네일로 생성 및 캐싱하여 제공.
  - `GET /api/file/{id}`: **모든 문서를 PDF로 통일하여 스트리밍.**
    - `DOCX` 요청 시, 실시간으로 PDF로 변환 후 제공.
    - `이미지 폴더` 요청 시, 모든 이미지를 단일 PDF로 묶어서 제공.
  - `GET /api/health`: 시스템 상태(DB, Watcher) 확인.

## 5. 핵심 프론트엔드 로직 (`frontend/`)

- **'하이브리드 렌더링' 성능 최적화 전략**:
  1.  **초기 로드**: `/api/search`로 메타데이터를 받고, `/api/thumbnail/{id}`을 호출해 **가벼운 썸네일 이미지만** 그리드에 즉시 표시.
  2.  **지연 로드 (Lazy Loading)**: 사용자가 썸네일에 마우스를 올리거나 클릭하면 이벤트 발생.
  3.  **동적 교체**: 해당 썸네일 `<img>` 컴포넌트를 실제 PDF 뷰어 (`react-pdf`) 컴포넌트로 교체.
  4.  **실시간 렌더링**: PDF 뷰어는 `/api/file/{id}` 엔드포인트를 통해 PDF 데이터를 스트리밍하여 렌더링.
  - **기대효과**: 수십 개의 무거운 문서를 동시에 로드하는 것을 방지하여 UI 프리징 현상을 원천적으로 해결하고 사용자 경험을 극대화.

## 6. 개발 워크플로우 및 명령어

- **의존성 설치**:
  ```bash
  # 프로젝트 루트에서 실행
  npm install
  # 백엔드 의존성 설치
  cd backend && uv pip install -r requirements.txt
  ```

- **개발 서버 실행**:
  ```bash
  # (예시) 루트 package.json에 정의된 스크립트 사용
  # 백엔드, 프론트엔드, Electron 동시 실행
  npm run dev
  ```

- **테스트**:
  ```bash
  # 백엔드 단위 테스트
  cd backend && pytest
  # 프론트엔드 단위 테스트
  cd frontend && npm test
  ```

- **빌드**:
  ```bash
  # Electron 앱으로 패키징 (.exe)
  npm run build
  ```

## 7. 중요 설정 파일

- `config/nas_paths.json`: **가장 중요한 설정 파일.** 파일 감시자가 모니터링할 NAS 폴더 경로 목록을 정의. 이 파일이 없으면 시스템이 동작하지 않음.
- `config/app_settings.json`: 앱의 기본 동작(정렬 순서, UI 테마 등)을 설정.
- `electron-builder.json`: Windows 설치 파일(.exe) 생성 관련 설정.
