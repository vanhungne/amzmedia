'use client';

import { useState } from 'react';
import ProgressBar from './ProgressBar';
import { ProgressState } from '@/lib/progressTracking';

interface BulkOperationModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  operationId: string | null;
  onComplete?: (state: ProgressState) => void;
}

export default function BulkOperationModal({
  isOpen,
  onClose,
  title,
  operationId,
  onComplete,
}: BulkOperationModalProps) {
  const [canClose, setCanClose] = useState(false);

  // Debug log
  if (!isOpen || !operationId) {
    if (process.env.NODE_ENV === 'development') {
      console.log('BulkOperationModal: Not showing', { isOpen, operationId });
    }
    return null;
  }

  const handleComplete = (state: ProgressState) => {
    setCanClose(true);
    onComplete?.(state);
  };

  const handleError = (state: ProgressState) => {
    setCanClose(true);
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-lg shadow-2xl p-6 max-w-2xl w-full mx-4 space-y-4 animate-slideInRight">
        {/* Header */}
        <div className="flex justify-between items-center border-b pb-4 mb-4">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <span className="text-blue-600">⚙️</span>
            {title}
          </h2>
          {canClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors p-1 hover:bg-gray-100 rounded"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Progress */}
        <div className="py-4">
          <ProgressBar
            operationId={operationId}
            onComplete={handleComplete}
            onError={handleError}
            showDetails={true}
          />
        </div>

        {/* Instructions */}
        {!canClose && (
          <div className="text-sm text-gray-700 bg-blue-50 border border-blue-200 p-4 rounded-lg flex items-start gap-2">
            <span className="text-blue-600 text-lg">ℹ️</span>
            <div>
              <p className="font-medium mb-1">Đang xử lý...</p>
              <p className="text-gray-600">Vui lòng đợi cho đến khi hoàn thành. Không đóng trang này.</p>
            </div>
          </div>
        )}

        {/* Close button */}
        {canClose && (
          <div className="flex justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Đóng
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

