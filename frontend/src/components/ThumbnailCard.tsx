'use client';

import React, { useState, useEffect } from 'react';
import { FileText, User, Hash, Calendar, Eye, Download, AlertCircle, ImageIcon } from 'lucide-react';

interface MedicalRecord {
  id: number;
  patient_name: string;
  patient_id: string;
  file_type: string;
  file_creation_date: string;
  file_size: number;
  parsing_confidence: number;
}

interface ThumbnailCardProps {
  record: MedicalRecord;
  isSelected: boolean;
  onView: () => void;
  onDownload: () => void;
  formatDate: (date: string) => string;
  formatFileSize: (bytes: number) => string;
  getFileTypeIcon: (fileType: string) => React.ReactElement;
  getConfidenceColor: (confidence: number) => string;
}

export default function ThumbnailCard({
  record,
  isSelected,
  onView,
  onDownload,
  formatDate,
  formatFileSize,
  getFileTypeIcon,
  getConfidenceColor
}: ThumbnailCardProps) {
  const [thumbnailUrl, setThumbnailUrl] = useState<string | null>(null);
  const [thumbnailLoading, setThumbnailLoading] = useState(true);
  const [thumbnailError, setThumbnailError] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [showPdfViewer, setShowPdfViewer] = useState(false);

  // 썸네일 로드 (PRD의 Thumbnail-First 전략)
  useEffect(() => {
    loadThumbnail();
  }, [record.id]);

  const loadThumbnail = async () => {
    try {
      setThumbnailLoading(true);
      setThumbnailError(false);

      const response = await fetch(`${process.env.BACKEND_URL}/api/thumbnail/${record.id}`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setThumbnailUrl(url);
      } else {
        setThumbnailError(true);
      }
    } catch (error) {
      console.error('Thumbnail load error:', error);
      setThumbnailError(true);
    } finally {
      setThumbnailLoading(false);
    }
  };

  // 컴포넌트 언마운트 시 썸네일 URL 정리
  useEffect(() => {
    return () => {
      if (thumbnailUrl) {
        URL.revokeObjectURL(thumbnailUrl);
      }
    };
  }, [thumbnailUrl]);

  // 마우스 호버 시 PDF 뷰어로 전환 (PRD의 하이브리드 렌더링)
  const handleMouseEnter = () => {
    setIsHovered(true);
    // PDF 뷰어 전환은 클릭 시에만 수행 (성능 고려)
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
  };

  const handleCardClick = () => {
    if (record.file_type === 'PDF' || record.file_type === 'DOCX') {
      setShowPdfViewer(true);
    }
    onView();
  };

  const renderThumbnail = () => {
    if (thumbnailLoading) {
      return (
        <div className="w-full h-48 bg-gray-100 rounded-lg flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    if (thumbnailError || !thumbnailUrl) {
      return (
        <div className="w-full h-48 bg-gray-100 rounded-lg flex flex-col items-center justify-center text-gray-400">
          {record.file_type === 'IMAGE_FOLDER' ? (
            <ImageIcon className="w-12 h-12 mb-2" />
          ) : (
            <FileText className="w-12 h-12 mb-2" />
          )}
          <span className="text-sm">썸네일 없음</span>
        </div>
      );
    }

    return (
      <div className="w-full h-48 bg-gray-100 rounded-lg overflow-hidden">
        <img
          src={thumbnailUrl}
          alt={`${record.patient_name} 썸네일`}
          className="w-full h-full object-cover transition-transform duration-200 hover:scale-105"
        />
      </div>
    );
  };

  const renderPdfViewer = () => {
    // TODO: react-pdf를 사용한 PDF 뷰어 구현
    // 현재는 placeholder 구현
    return (
      <div className="w-full h-48 bg-gray-900 rounded-lg flex items-center justify-center text-white">
        <div className="text-center">
          <FileText className="w-12 h-12 mx-auto mb-2" />
          <p className="text-sm">PDF 뷰어</p>
          <p className="text-xs text-gray-300">구현 예정</p>
        </div>
      </div>
    );
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-md border transition-all duration-200 hover:shadow-lg ${
        isSelected ? 'ring-2 ring-blue-500 border-blue-300' : 'border-gray-200'
      } ${isHovered ? 'transform -translate-y-1' : ''}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      {/* 썸네일 영역 */}
      <div 
        className="p-4 cursor-pointer"
        onClick={handleCardClick}
      >
        {showPdfViewer && (record.file_type === 'PDF' || record.file_type === 'DOCX') 
          ? renderPdfViewer() 
          : renderThumbnail()
        }
      </div>

      {/* 정보 영역 */}
      <div className="p-4 pt-0">
        {/* 환자 정보 */}
        <div className="mb-3">
          <div className="flex items-center mb-1">
            <User className="w-4 h-4 text-gray-400 mr-2" />
            <h3 className="font-semibold text-gray-900 truncate">{record.patient_name}</h3>
          </div>
          <div className="flex items-center text-sm text-gray-600">
            <Hash className="w-4 h-4 text-gray-400 mr-2" />
            <span>{record.patient_id}</span>
          </div>
        </div>

        {/* 파일 정보 */}
        <div className="space-y-2 mb-3">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center">
              {getFileTypeIcon(record.file_type)}
              <span className="ml-2 text-gray-600">{record.file_type}</span>
            </div>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(record.parsing_confidence)}`}>
              {Math.round(record.parsing_confidence * 100)}%
            </span>
          </div>
          
          <div className="flex items-center text-sm text-gray-600">
            <Calendar className="w-4 h-4 text-gray-400 mr-2" />
            <span className="truncate">{formatDate(record.file_creation_date)}</span>
          </div>
          
          <div className="text-sm text-gray-600">
            크기: {formatFileSize(record.file_size)}
          </div>
        </div>

        {/* 액션 버튼들 */}
        <div className="flex space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onView();
            }}
            className="flex-1 flex items-center justify-center space-x-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Eye className="w-4 h-4" />
            <span>보기</span>
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDownload();
            }}
            className="flex items-center justify-center px-3 py-2 text-sm text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* 호버 시 추가 정보 오버레이 */}
      {isHovered && (
        <div className="absolute top-2 right-2 bg-black bg-opacity-75 text-white text-xs px-2 py-1 rounded">
          클릭하여 상세보기
        </div>
      )}
    </div>
  );
} 