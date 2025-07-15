'use client';

import { useState, KeyboardEvent } from 'react';
import { Search, Filter, SortAsc, SortDesc, Calendar } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string, filters?: SearchFilters) => void;
  loading?: boolean;
  placeholder?: string;
}

interface SearchFilters {
  fileType?: string;
  dateRange?: {
    start?: string;
    end?: string;
  };
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export default function SearchBar({ onSearch, loading = false, placeholder = '검색어를 입력하세요...' }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    fileType: '',
    dateRange: {},
    sortBy: 'file_creation_date',
    sortOrder: 'desc'
  });

  const handleSearch = () => {
    onSearch(query, filters);
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleFilterChange = (key: keyof SearchFilters, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    
    // 실시간 필터링 (검색어가 있을 때만)
    if (query.trim()) {
      onSearch(query, newFilters);
    }
  };

  return (
    <div className="space-y-4">
      {/* 메인 검색 바 */}
      <div className="flex items-center space-x-4">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={loading}
            className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
        
        <button
          onClick={handleSearch}
          disabled={loading || !query.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>검색중...</span>
            </div>
          ) : (
            '검색'
          )}
        </button>
        
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`p-3 rounded-lg border border-gray-300 transition-colors ${
            showFilters ? 'bg-blue-50 border-blue-300 text-blue-600' : 'bg-white text-gray-600 hover:bg-gray-50'
          }`}
          title="필터 및 정렬 옵션"
        >
          <Filter className="h-5 w-5" />
        </button>
      </div>

      {/* 필터 영역 */}
      {showFilters && (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* 파일 형식 필터 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                파일 형식
              </label>
              <select
                value={filters.fileType || ''}
                onChange={(e) => handleFilterChange('fileType', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">전체</option>
                <option value="PDF">PDF</option>
                <option value="DOCX">DOCX</option>
                <option value="IMAGE_FOLDER">이미지 폴더</option>
              </select>
            </div>

            {/* 정렬 기준 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                정렬 기준
              </label>
              <select
                value={filters.sortBy || 'file_creation_date'}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="file_creation_date">파일 생성일</option>
                <option value="patient_name">환자명</option>
                <option value="created_at">등록일</option>
              </select>
            </div>

            {/* 정렬 순서 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                정렬 순서
              </label>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleFilterChange('sortOrder', 'desc')}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md border transition-colors ${
                    filters.sortOrder === 'desc' 
                      ? 'bg-blue-100 border-blue-300 text-blue-700' 
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <SortDesc className="w-4 h-4" />
                  <span>내림차순</span>
                </button>
                <button
                  onClick={() => handleFilterChange('sortOrder', 'asc')}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-md border transition-colors ${
                    filters.sortOrder === 'asc' 
                      ? 'bg-blue-100 border-blue-300 text-blue-700' 
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <SortAsc className="w-4 h-4" />
                  <span>오름차순</span>
                </button>
              </div>
            </div>

            {/* 날짜 범위 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="w-4 h-4 inline mr-1" />
                날짜 범위
              </label>
              <div className="space-y-2">
                <input
                  type="date"
                  value={filters.dateRange?.start || ''}
                  onChange={(e) => handleFilterChange('dateRange', { 
                    ...filters.dateRange, 
                    start: e.target.value 
                  })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder="시작 날짜"
                />
                <input
                  type="date"
                  value={filters.dateRange?.end || ''}
                  onChange={(e) => handleFilterChange('dateRange', { 
                    ...filters.dateRange, 
                    end: e.target.value 
                  })}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder="종료 날짜"
                />
              </div>
            </div>
          </div>

          {/* 필터 리셋 버튼 */}
          <div className="flex justify-end mt-4">
            <button
              onClick={() => {
                const resetFilters = {
                  fileType: '',
                  dateRange: {},
                  sortBy: 'file_creation_date',
                  sortOrder: 'desc' as const
                };
                setFilters(resetFilters);
                if (query.trim()) {
                  onSearch(query, resetFilters);
                }
              }}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
            >
              필터 초기화
            </button>
          </div>
        </div>
      )}
    </div>
  );
} 