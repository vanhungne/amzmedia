/**
 * Progress Tracking System
 * Hệ thống theo dõi tiến trình cho các operations lớn
 */

export interface ProgressState {
  operationId: string;
  progress: number; // 0-100
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message?: string;
  currentItem?: number;
  totalItems?: number;
  errors?: Array<{ item: string; error: string }>;
  startedAt?: Date;
  completedAt?: Date;
}

// In-memory store cho progress tracking
const progressStore = new Map<string, ProgressState>();

/**
 * Tạo một operation mới
 */
export function createOperation(operationId: string, totalItems: number): ProgressState {
  const state: ProgressState = {
    operationId,
    progress: 0,
    status: 'pending',
    currentItem: 0,
    totalItems,
    errors: [],
    startedAt: new Date(),
  };
  
  progressStore.set(operationId, state);
  return state;
}

/**
 * Cập nhật progress của operation
 */
export function updateProgress(
  operationId: string,
  currentItem: number,
  message?: string
): ProgressState | null {
  const state = progressStore.get(operationId);
  if (!state) return null;

  const progress = state.totalItems 
    ? Math.round((currentItem / state.totalItems) * 100)
    : 0;

  const updatedState: ProgressState = {
    ...state,
    progress,
    currentItem,
    message,
    status: 'processing',
  };

  progressStore.set(operationId, updatedState);
  return updatedState;
}

/**
 * Đánh dấu operation hoàn thành
 */
export function completeOperation(
  operationId: string,
  message?: string
): ProgressState | null {
  const state = progressStore.get(operationId);
  if (!state) return null;

  const updatedState: ProgressState = {
    ...state,
    progress: 100,
    status: 'completed',
    message: message || 'Hoàn thành!',
    completedAt: new Date(),
  };

  progressStore.set(operationId, updatedState);
  
  // Auto cleanup after 15 minutes (increased from 5 minutes to give more time for polling)
  setTimeout(() => {
    console.log(`[ProgressTracking] Auto-cleaning up completed operation: ${operationId}`);
    progressStore.delete(operationId);
  }, 15 * 60 * 1000);

  return updatedState;
}

/**
 * Đánh dấu operation thất bại
 */
export function failOperation(
  operationId: string,
  message: string
): ProgressState | null {
  const state = progressStore.get(operationId);
  if (!state) return null;

  const updatedState: ProgressState = {
    ...state,
    status: 'failed',
    message,
    completedAt: new Date(),
  };

  progressStore.set(operationId, updatedState);
  
  // Auto cleanup after 20 minutes (increased from 10 minutes)
  setTimeout(() => {
    console.log(`[ProgressTracking] Auto-cleaning up failed operation: ${operationId}`);
    progressStore.delete(operationId);
  }, 20 * 60 * 1000);

  return updatedState;
}

/**
 * Thêm error vào operation
 */
export function addError(
  operationId: string,
  item: string,
  error: string
): ProgressState | null {
  const state = progressStore.get(operationId);
  if (!state) return null;

  const updatedState: ProgressState = {
    ...state,
    errors: [...(state.errors || []), { item, error }],
  };

  progressStore.set(operationId, updatedState);
  return updatedState;
}

/**
 * Lấy trạng thái hiện tại của operation
 */
export function getProgress(operationId: string): ProgressState | null {
  return progressStore.get(operationId) || null;
}

/**
 * Xóa operation khỏi store
 */
export function deleteOperation(operationId: string): boolean {
  return progressStore.delete(operationId);
}

/**
 * Lấy tất cả operations đang chạy
 */
export function getAllOperations(): ProgressState[] {
  return Array.from(progressStore.values());
}

/**
 * Helper: Generate unique operation ID
 */
export function generateOperationId(prefix: string = 'op'): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Helper: Format thời gian thực thi
 */
export function formatDuration(startedAt?: Date, completedAt?: Date): string {
  if (!startedAt) return 'N/A';
  
  const end = completedAt || new Date();
  const duration = end.getTime() - startedAt.getTime();
  
  const seconds = Math.floor(duration / 1000);
  const minutes = Math.floor(seconds / 60);
  
  if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  }
  return `${seconds}s`;
}

/**
 * Helper: Estimate thời gian còn lại
 */
export function estimateTimeRemaining(state: ProgressState): string {
  if (!state.startedAt || !state.currentItem || !state.totalItems) {
    return 'Đang tính...';
  }

  const elapsed = Date.now() - state.startedAt.getTime();
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

/**
 * Helper: Retry a function with exponential backoff
 * @param fn Function to retry
 * @param maxRetries Maximum number of retries (default: 3)
 * @param initialDelay Initial delay in ms (default: 100)
 * @returns Result of the function
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  initialDelay: number = 100
): Promise<T> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error: any) {
      lastError = error;
      
      // Don't retry on last attempt
      if (attempt === maxRetries) {
        break;
      }
      
      // Exponential backoff: delay = initialDelay * 2^attempt
      const delay = initialDelay * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError || new Error('Retry failed');
}

