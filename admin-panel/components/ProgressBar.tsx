'use client';

import { useEffect, useState } from 'react';
import { ProgressState } from '@/lib/progressTracking';

interface ProgressBarProps {
  operationId: string;
  onComplete?: (state: ProgressState) => void;
  onError?: (state: ProgressState) => void;
  pollInterval?: number; // milliseconds
  showDetails?: boolean;
}

export default function ProgressBar({
  operationId,
  onComplete,
  onError,
  pollInterval = 500,
  showDetails = true,
}: ProgressBarProps) {
  const [progress, setProgress] = useState<ProgressState | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    if (!isPolling || !operationId) return;

    const poll = async () => {
      try {
        const res = await fetch(`/api/operations/${encodeURIComponent(operationId)}/status`);
        if (!res.ok) {
          if (res.status === 404) {
            // Operation not found - stop polling immediately to avoid spam
            console.log('[ProgressBar] Operation not found, stopping poll:', operationId);
            const errorData = await res.json().catch(() => ({}));
            
            // If operation is not found, assume it might be completed
            // Create a completed state to show success
            const completedState: ProgressState = {
              operationId,
              progress: 100,
              status: 'completed',
              message: 'Operation completed (may have been cleaned up)',
              currentItem: 0,
              totalItems: 0,
              completedAt: new Date(),
            };
            
            setProgress(completedState);
            setIsPolling(false);
            onComplete?.(completedState);
            return;
          } else {
            console.error('[ProgressBar] Failed to fetch progress:', res.status, res.statusText);
            setIsPolling(false);
            return;
          }
        }

        const data = await res.json();
        
        // Convert ISO strings back to Date objects
        const state: ProgressState = {
          ...data,
          startedAt: data.startedAt ? new Date(data.startedAt) : undefined,
          completedAt: data.completedAt ? new Date(data.completedAt) : undefined,
        };
        
        setProgress(state);

        // Stop polling khi hoàn thành hoặc thất bại
        if (state.status === 'completed') {
          setIsPolling(false);
          onComplete?.(state);
        } else if (state.status === 'failed') {
          setIsPolling(false);
          onError?.(state);
        }
      } catch (error: any) {
        console.error('[ProgressBar] Error polling progress:', error);
        // Don't stop polling on network errors, might be temporary
        // But log the error for debugging
        if (error.message?.includes('fetch')) {
          console.warn('[ProgressBar] Network error, will retry...');
        }
      }
    };

    // Initial poll immediately
    poll();

    // Set up interval
    const interval = setInterval(poll, pollInterval);

    return () => clearInterval(interval);
  }, [operationId, pollInterval, isPolling, onComplete, onError]);

  if (!progress) {
    return (
      <div className="w-full bg-gray-200 rounded-full h-2.5 animate-pulse">
        <div className="bg-blue-600 h-2.5 rounded-full w-0"></div>
      </div>
    );
  }

  const getStatusColor = () => {
    switch (progress.status) {
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'processing':
        return 'bg-blue-500';
      default:
        return 'bg-gray-400';
    }
  };

  const getStatusText = () => {
    switch (progress.status) {
      case 'completed':
        return '✅ Hoàn thành';
      case 'failed':
        return '❌ Thất bại';
      case 'processing':
        return '⚙️ Đang xử lý...';
      case 'pending':
        return '⏳ Đang chuẩn bị...';
    }
  };

  return (
    <div className="w-full space-y-3">
      {/* Progress Bar - Large and Visible */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">Tiến trình</span>
          <span className="text-lg font-bold text-blue-600">{progress.progress}%</span>
        </div>
        
        <div className="relative w-full bg-gray-200 rounded-full h-6 overflow-hidden shadow-inner">
          <div
            className={`h-full transition-all duration-500 ease-out ${getStatusColor()} flex items-center justify-end pr-2`}
            style={{ width: `${Math.max(0, Math.min(100, progress.progress))}%` }}
          >
            {/* Animated shimmer effect */}
            {progress.status === 'processing' && (
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
            )}
            
            {/* Percentage text inside bar (only if > 15%) */}
            {progress.progress > 15 && (
              <span className="text-xs font-bold text-white z-10">
                {progress.progress}%
              </span>
            )}
          </div>
          
          {/* Percentage text outside bar (if < 15%) */}
          {progress.progress <= 15 && (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-xs font-semibold text-gray-700">
                {progress.progress}%
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Details */}
      {showDetails && (
        <div className="space-y-1 text-sm">
          {/* Status */}
          <div className="flex justify-between items-center">
            <span className="font-medium">{getStatusText()}</span>
            {progress.currentItem !== undefined && progress.totalItems !== undefined && (
              <span className="text-gray-600">
                {progress.currentItem} / {progress.totalItems}
              </span>
            )}
          </div>

          {/* Message */}
          {progress.message && (
            <div className="text-gray-600 italic">
              {progress.message}
            </div>
          )}

          {/* Time estimate */}
          {progress.status === 'processing' && progress.currentItem && progress.totalItems && progress.startedAt && (
            <div className="text-gray-500 text-xs">
              Ước tính còn lại: {estimateTimeRemaining(progress)}
            </div>
          )}

          {/* Errors */}
          {progress.errors && progress.errors.length > 0 && (
            <details className="mt-2">
              <summary className="cursor-pointer text-red-600 font-medium">
                {progress.errors.length} lỗi xảy ra
              </summary>
              <div className="mt-2 space-y-1 max-h-40 overflow-y-auto bg-red-50 p-2 rounded">
                {progress.errors.map((err, idx) => (
                  <div key={idx} className="text-xs text-red-700">
                    <span className="font-medium">{err.item}:</span> {err.error}
                  </div>
                ))}
              </div>
            </details>
          )}

          {/* Duration */}
          {(progress.status === 'completed' || progress.status === 'failed') && progress.startedAt && progress.completedAt && (
            <div className="text-gray-500 text-xs">
              Thời gian: {formatDuration(new Date(progress.startedAt), new Date(progress.completedAt))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Helper functions (local copies)
function estimateTimeRemaining(state: ProgressState): string {
  if (!state.startedAt || !state.currentItem || !state.totalItems) {
    return 'Đang tính...';
  }

  const elapsed = Date.now() - new Date(state.startedAt).getTime();
  const avgTimePerItem = elapsed / state.currentItem;
  const remainingItems = state.totalItems - state.currentItem;
  const estimatedMs = avgTimePerItem * remainingItems;

  const seconds = Math.ceil(estimatedMs / 1000);
  const minutes = Math.floor(seconds / 60);

  if (minutes > 0) {
    return `~${minutes}m ${seconds % 60}s`;
  }
  return `~${seconds}s`;
}

function formatDuration(startedAt: Date, completedAt: Date): string {
  const duration = completedAt.getTime() - startedAt.getTime();
  const seconds = Math.floor(duration / 1000);
  const minutes = Math.floor(seconds / 60);

  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  }
  return `${seconds}s`;
}

// Add shimmer animation to globals.css

