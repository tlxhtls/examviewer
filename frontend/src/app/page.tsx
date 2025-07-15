'use client';

import { useState, useEffect } from 'react';
import { Search, Filter, Grid, List, Settings, RefreshCw } from 'lucide-react';
import SearchBar from '@/components/SearchBar';
import ResultsGrid from '@/components/ResultsGrid';
import StatusBar from '@/components/StatusBar';
import LoadingSpinner from '@/components/LoadingSpinner';

interface MedicalRecord {
  id: number;
  patient_name: string;
  patient_id: string;
  file_type: string;
  file_creation_date: string;
  file_size: number;
  parsing_confidence: number;
}

interface SearchResult {
  total: number;
  results: MedicalRecord[];
  query: string;
  limit: number;
  offset: number;
}

export default function Home() {
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentQuery, setCurrentQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [gridColumns, setGridColumns] = useState(4);

  // 백엔드 상태 확인
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${process.env.BACKEND_URL}/api/health`);
      if (response.ok) {
        setBackendStatus('connected');
      } else {
        setBackendStatus('disconnected');
      }
    } catch (error) {
      setBackendStatus('disconnected');
      console.error('Backend health check failed:', error);
    }
  };

  const handleSearch = async (query: string, filters?: any) => {
    if (!query.trim()) {
      setSearchResults(null);
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentQuery(query);

    try {
      const response = await fetch(
        `${process.env.BACKEND_URL}/api/search?q=${encodeURIComponent(query)}&limit=50&offset=0`
      );

      if (!response.ok) {
        throw new Error(`검색 실패: ${response.status}`);
      }

      const data: SearchResult = await response.json();
      setSearchResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '검색 중 오류가 발생했습니다.');
      setSearchResults(null);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    if (currentQuery) {
      handleSearch(currentQuery);
    }
    checkBackendHealth();
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* 상단 헤더 */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-gray-900">
              환자 검사 통합 뷰어
            </h1>
            <div className="flex items-center space-x-2">
              <div 
                className={`w-2 h-2 rounded-full ${
                  backendStatus === 'connected' ? 'bg-green-500' : 
                  backendStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500'
                }`}
              />
              <span className="text-sm text-gray-600">
                {backendStatus === 'connected' ? '연결됨' : 
                 backendStatus === 'disconnected' ? '연결 끊김' : '확인 중...'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleRefresh}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="새로고침"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded transition-colors ${
                  viewMode === 'grid' 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
                title="그리드 보기"
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded transition-colors ${
                  viewMode === 'list' 
                    ? 'bg-white text-blue-600 shadow-sm' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
                title="목록 보기"
              >
                <List className="w-4 h-4" />
              </button>
            </div>
            
            <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* 검색 영역 */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <SearchBar 
          onSearch={handleSearch}
          loading={loading}
          placeholder="환자명 또는 등록번호를 입력하세요..."
        />
      </div>

      {/* 메인 컨텐츠 영역 */}
      <main className="flex-1 overflow-hidden">
        {loading && (
          <div className="flex items-center justify-center h-full">
            <LoadingSpinner message="검색 중..." />
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="text-red-500 text-lg mb-2">오류 발생</div>
              <div className="text-gray-600">{error}</div>
              <button
                onClick={handleRefresh}
                className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                다시 시도
              </button>
            </div>
          </div>
        )}

        {!loading && !error && searchResults && (
          <ResultsGrid 
            results={searchResults}
            viewMode={viewMode}
            columns={gridColumns}
          />
        )}

        {!loading && !error && !searchResults && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <Search className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h2 className="text-xl font-medium mb-2">검색을 시작하세요</h2>
              <p>환자명 또는 등록번호를 입력하여 검사 결과를 찾아보세요.</p>
            </div>
          </div>
        )}
      </main>

      {/* 하단 상태 바 */}
      <StatusBar 
        results={searchResults}
        backendStatus={backendStatus}
      />
    </div>
  );
}
