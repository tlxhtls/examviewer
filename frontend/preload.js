const { contextBridge, ipcRenderer } = require('electron');

// 렌더러 프로세스에서 사용할 안전한 API 노출
contextBridge.exposeInMainWorld('electronAPI', {
  // 플랫폼 정보
  platform: process.platform,
  
  // 버전 정보
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron
  },
  
  // 파일 시스템 관련 (향후 확장용)
  fileSystem: {
    // 안전한 파일 조작 API 추가 예정
  },
  
  // 환경 정보
  isDev: process.env.NODE_ENV === 'development'
});

// 보안 강화: 노드 모듈 접근 차단
delete window.require;
delete window.exports;
delete window.module; 