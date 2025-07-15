'use client';

import { useState, useEffect } from 'react';
import { FileText, Calendar, User, Hash, Eye, Download, AlertCircle } from 'lucide-react';
import ThumbnailCard from './ThumbnailCard';

interface MedicalRecord {
  id: number;
  patient_name: string;
  patient_id: string;
  file_type: string;
  file_creation_date: string;
  file_size: number;
  parsing_confidence: number;
}

interface ResultsGridProps {
  results: {
    total: number;
    results: MedicalRecord[];
    query: string;
    limit: number;
    offset: number;
  };
  viewMode: 'grid' | 'list';
  columns?: number;
}

export default function ResultsGrid({ results, viewMode, columns = 4 }: ResultsGridProps) {
  const [selectedRecord, setSelectedRecord] = useState<number | null>(null);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (bytes: number) => {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  const getFileTypeIcon = (fileType: string) => {
    switch (fileType) {
      case 'PDF':
        return <FileText className="w-5 h-5 text-red-500" />;
      case 'DOCX':
        return <FileText className="w-5 h-5 text-blue-500" />;
      case 'IMAGE_FOLDER':
        return <FileText className="w-5 h-5 text-green-500" />;
      default:
        return <FileText className="w-5 h-5 text-gray-500" />;
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600 bg-green-100';
    if (confidence >= 0.7) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const handleViewFile = async (recordId: number) => {
    // TODO: 파일 보기 로직 구현
    console.log('View file:', recordId);
    setSelectedRecord(recordId);
  };

  const handleDownloadFile = async (recordId: number, fileName: string) => {
    try {
      const response = await fetch(`${process.env.BACKEND_URL}/api/file/${recordId}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        throw new Error('파일 다운로드 실패');
      }
    } catch (error) {
      console.error('Download error:', error);
      alert('파일 다운로드 중 오류가 발생했습니다.');
    }
  };

  if (results.results.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-500">
          <AlertCircle className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium mb-2">검색 결과가 없습니다</h3>
          <p>다른 검색어를 시도해보세요.</p>
        </div>
      </div>
    );
  }

  // 그리드 뷰 렌더링
  if (viewMode === 'grid') {
    return (
      <div className="p-6 h-full overflow-auto">
        <div 
          className={`grid gap-6 ${
            columns === 2 ? 'grid-cols-2' :
            columns === 3 ? 'grid-cols-3' :
            columns === 4 ? 'grid-cols-4' :
            columns === 5 ? 'grid-cols-5' :
            'grid-cols-6'
          }`}
          style={{
            gridTemplateColumns: `repeat(${columns}, minmax(250px, 1fr))`
          }}
        >
          {results.results.map((record) => (
            <ThumbnailCard
              key={record.id}
              record={record}
              isSelected={selectedRecord === record.id}
              onView={() => handleViewFile(record.id)}
              onDownload={() => handleDownloadFile(record.id, `${record.patient_name}_${record.patient_id}.${record.file_type.toLowerCase()}`)}
              formatDate={formatDate}
              formatFileSize={formatFileSize}
              getFileTypeIcon={getFileTypeIcon}
              getConfidenceColor={getConfidenceColor}
            />
          ))}
        </div>
      </div>
    );
  }

  // 목록 뷰 렌더링
  return (
    <div className="h-full overflow-auto">
      <div className="bg-white">
        {/* 테이블 헤더 */}
        <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-gray-50 border-b border-gray-200 text-sm font-medium text-gray-700">
          <div className="col-span-1">유형</div>
          <div className="col-span-2">환자명</div>
          <div className="col-span-2">등록번호</div>
          <div className="col-span-2">생성일</div>
          <div className="col-span-1">크기</div>
          <div className="col-span-1">신뢰도</div>
          <div className="col-span-3">작업</div>
        </div>

        {/* 테이블 내용 */}
        <div className="divide-y divide-gray-200">
          {results.results.map((record) => (
            <div 
              key={record.id} 
              className={`grid grid-cols-12 gap-4 px-6 py-4 hover:bg-gray-50 transition-colors ${
                selectedRecord === record.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
              }`}
            >
              {/* 파일 유형 */}
              <div className="col-span-1 flex items-center">
                {getFileTypeIcon(record.file_type)}
              </div>

              {/* 환자명 */}
              <div className="col-span-2 flex items-center">
                <User className="w-4 h-4 text-gray-400 mr-2" />
                <span className="font-medium text-gray-900">{record.patient_name}</span>
              </div>

              {/* 등록번호 */}
              <div className="col-span-2 flex items-center">
                <Hash className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-gray-600">{record.patient_id}</span>
              </div>

              {/* 생성일 */}
              <div className="col-span-2 flex items-center">
                <Calendar className="w-4 h-4 text-gray-400 mr-2" />
                <span className="text-gray-600">{formatDate(record.file_creation_date)}</span>
              </div>

              {/* 파일 크기 */}
              <div className="col-span-1 flex items-center">
                <span className="text-gray-600">{formatFileSize(record.file_size)}</span>
              </div>

              {/* 신뢰도 */}
              <div className="col-span-1 flex items-center">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(record.parsing_confidence)}`}>
                  {Math.round(record.parsing_confidence * 100)}%
                </span>
              </div>

              {/* 작업 버튼들 */}
              <div className="col-span-3 flex items-center space-x-2">
                <button
                  onClick={() => handleViewFile(record.id)}
                  className="flex items-center space-x-1 px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                >
                  <Eye className="w-4 h-4" />
                  <span>보기</span>
                </button>
                <button
                  onClick={() => handleDownloadFile(record.id, `${record.patient_name}_${record.patient_id}.${record.file_type.toLowerCase()}`)}
                  className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>다운로드</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 