# 환자 검사 통합 뷰어 (Patient Exam Viewer)

복수의 NAS에 분산 저장된 환자 검사 결과를 통합 검색하고 동시 미리보기할 수 있는 데스크톱 애플리케이션

## 🚀 주요 기능

- **통합 검색**: 여러 NAS에 분산된 환자 검사 파일을 한 번에 검색
- **실시간 동기화**: 파일 변경사항을 실시간으로 자동 반영
- **하이브리드 렌더링**: 썸네일 우선 로딩 후 인터랙션 시 PDF 뷰어 전환
- **다양한 파일 형식 지원**: PDF, DOCX, 이미지 폴더 등 자동 변환 및 처리

## 🏗️ 시스템 아키텍처

- **프론트엔드**: Electron + Next.js + TypeScript + Tailwind CSS
- **백엔드**: Python FastAPI + SQLite
- **파일 감시**: Watchdog를 이용한 실시간 모니터링
- **의존성 관리**: UV (Python), npm/yarn (Node.js)

## 📁 프로젝트 구조

```
/patient-viewer-app/
├── backend/          # FastAPI 백엔드
├── frontend/         # Electron + Next.js 프론트엔드
├── docs/            # 프로젝트 문서
├── config/          # 설정 파일
├── backup/          # 백업 파일
└── PRD.md          # 제품 요구사항 문서
```

## 🛠️ 개발 환경 설정

### 백엔드 (Python + FastAPI)

```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

### 프론트엔드 (Electron + Next.js)

```bash
cd frontend
npm install
npm run dev
```

## 📖 문서

자세한 개발 계획과 요구사항은 [PRD.md](./PRD.md)를 참조하세요.

## 🔧 개발 상태

- [x] 프로젝트 구조 설정
- [ ] 백엔드 핵심 기능 개발
- [ ] 프론트엔드 기본 구조 개발
- [ ] 고급 기능 통합
- [ ] 배포 및 안정화

## 📝 라이선스

이 프로젝트는 의료기관 내부 사용을 위해 개발되었습니다.

---

**개발 팀**: tlxhtls  
**최종 업데이트**: 2025년 1월 15일 