'use client';

import { Clock, Database, Server, FileText } from 'lucide-react';

interface StatusBarProps {
  results?: {
    total: number;
    results: any[];
    query: string;
  } | null;
  backendStatus: 'checking' | 'connected' | 'disconnected';
}

export default function StatusBar({ results, backendStatus }: StatusBarProps) {
  const formatFileSize = (bytes?: number) => {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  const getCurrentTime = () => {
    return new Date().toLocaleTimeString('ko-KR');
  };

  return (
    <footer className="bg-white border-t border-gray-200 px-6 py-2">
      <div className="flex items-center justify-between text-sm text-gray-600">
        {/* 왼쪽: 검색 결과 정보 */}
        <div className="flex items-center space-x-6">
          {results ? (
            <>
              <div className="flex items-center space-x-1">
                <FileText className="w-4 h-4" />
                <span>
                  총 <span className="font-medium text-gray-900">{results.total}</span>개 결과
                  {results.results.length < results.total && (
                    <span className="text-gray-500"> (표시: {results.results.length}개)</span>
                  )}
                </span>
              </div>
              
              {results.query && (
                <div className="text-gray-500">
                  검색어: <span className="font-medium">"{results.query}"</span>
                </div>
              )}
            </>
          ) : (
            <div className="text-gray-500">검색 대기 중</div>
          )}
        </div>

        {/* 오른쪽: 시스템 상태 */}
        <div className="flex items-center space-x-6">
          {/* 백엔드 연결 상태 */}
          <div className="flex items-center space-x-1">
            <Server className="w-4 h-4" />
            <span>백엔드:</span>
            <div className="flex items-center space-x-1">
              <div 
                className={`w-2 h-2 rounded-full ${
                  backendStatus === 'connected' ? 'bg-green-500' : 
                  backendStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
                }`}
              />
              <span className={`font-medium ${
                backendStatus === 'connected' ? 'text-green-600' : 
                backendStatus === 'disconnected' ? 'text-red-600' : 'text-yellow-600'
              }`}>
                {backendStatus === 'connected' ? '연결됨' : 
                 backendStatus === 'disconnected' ? '연결 끊김' : '확인 중...'}
              </span>
            </div>
          </div>

          {/* 현재 시간 */}
          <div className="flex items-center space-x-1">
            <Clock className="w-4 h-4" />
            <span>{getCurrentTime()}</span>
          </div>

          {/* 버전 정보 */}
          <div className="text-gray-500">
            v1.0.0
          </div>
        </div>
      </div>
    </footer>
  );
} 