/**
 * Performance Monitoring & Optimization Utilities
 */

/**
 * Measure and log performance of async functions
 */
export async function measurePerformance<T>(
  name: string,
  fn: () => Promise<T>,
  logThreshold: number = 1000 // Log warning if slower than 1s
): Promise<T> {
  const start = performance.now();
  
  try {
    const result = await fn();
    const duration = performance.now() - start;
    
    logPerformance(name, duration, logThreshold);
    
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    console.error(`[Performance Error] ${name}: ${duration.toFixed(2)}ms`, error);
    throw error;
  }
}

/**
 * Measure sync function performance
 */
export function measureSync<T>(
  name: string,
  fn: () => T,
  logThreshold: number = 100
): T {
  const start = performance.now();
  
  try {
    const result = fn();
    const duration = performance.now() - start;
    
    logPerformance(name, duration, logThreshold);
    
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    console.error(`[Performance Error] ${name}: ${duration.toFixed(2)}ms`, error);
    throw error;
  }
}

/**
 * Log performance metrics
 */
function logPerformance(name: string, duration: number, threshold: number) {
  const formatted = duration.toFixed(2);
  
  if (duration > threshold) {
    console.warn(`⚠️ [Slow Operation] ${name}: ${formatted}ms`);
  } else {
    console.log(`✅ [Performance] ${name}: ${formatted}ms`);
  }
  
  // Send to analytics (implement your analytics here)
  // analytics.track('performance', { name, duration });
}

/**
 * Batch multiple requests into one
 */
export class RequestBatcher<T, R> {
  private queue: Array<{
    input: T;
    resolve: (value: R) => void;
    reject: (error: any) => void;
  }> = [];
  
  private timeout: NodeJS.Timeout | null = null;
  private batchDelay: number;
  private batchFn: (inputs: T[]) => Promise<R[]>;

  constructor(
    batchFn: (inputs: T[]) => Promise<R[]>,
    batchDelay: number = 50 // 50ms delay
  ) {
    this.batchFn = batchFn;
    this.batchDelay = batchDelay;
  }

  /**
   * Add request to batch
   */
  request(input: T): Promise<R> {
    return new Promise((resolve, reject) => {
      this.queue.push({ input, resolve, reject });

      if (this.timeout) {
        clearTimeout(this.timeout);
      }

      this.timeout = setTimeout(() => {
        this.flush();
      }, this.batchDelay);
    });
  }

  /**
   * Flush the batch
   */
  private async flush() {
    if (this.queue.length === 0) return;

    const batch = [...this.queue];
    this.queue = [];
    this.timeout = null;

    try {
      const inputs = batch.map(item => item.input);
      const results = await this.batchFn(inputs);

      batch.forEach((item, index) => {
        item.resolve(results[index]);
      });
    } catch (error) {
      batch.forEach(item => {
        item.reject(error);
      });
    }
  }
}

/**
 * Rate limiter
 */
export class RateLimiter {
  private tokens: number;
  private lastRefill: number;
  private maxTokens: number;
  private refillRate: number; // tokens per second

  constructor(maxTokens: number, refillRate: number) {
    this.maxTokens = maxTokens;
    this.tokens = maxTokens;
    this.refillRate = refillRate;
    this.lastRefill = Date.now();
  }

  /**
   * Try to consume tokens
   */
  async consume(tokens: number = 1): Promise<void> {
    this.refill();

    while (this.tokens < tokens) {
      const waitTime = ((tokens - this.tokens) / this.refillRate) * 1000;
      await new Promise(resolve => setTimeout(resolve, waitTime));
      this.refill();
    }

    this.tokens -= tokens;
  }

  /**
   * Refill tokens based on time passed
   */
  private refill() {
    const now = Date.now();
    const timePassed = (now - this.lastRefill) / 1000;
    const tokensToAdd = timePassed * this.refillRate;

    this.tokens = Math.min(this.maxTokens, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }

  /**
   * Get available tokens
   */
  getAvailableTokens(): number {
    this.refill();
    return Math.floor(this.tokens);
  }
}

/**
 * Retry with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: any;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (i < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, i);
        console.log(`Retry ${i + 1}/${maxRetries} after ${delay}ms`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}

/**
 * Timeout wrapper
 */
export async function withTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number,
  errorMessage: string = 'Operation timed out'
): Promise<T> {
  const timeoutPromise = new Promise<never>((_, reject) => {
    setTimeout(() => reject(new Error(errorMessage)), timeoutMs);
  });

  return Promise.race([promise, timeoutPromise]);
}

/**
 * Parallel execution with limit
 */
export async function parallelLimit<T, R>(
  items: T[],
  fn: (item: T) => Promise<R>,
  limit: number = 5
): Promise<R[]> {
  const results: R[] = [];
  const executing: Promise<void>[] = [];

  for (const item of items) {
    const promise = fn(item).then(result => {
      results.push(result);
    });

    executing.push(promise);

    if (executing.length >= limit) {
      await Promise.race(executing);
      executing.splice(
        executing.findIndex(p => p === promise),
        1
      );
    }
  }

  await Promise.all(executing);
  return results;
}

/**
 * Chunk array for batch processing
 */
export function chunk<T>(array: T[], size: number): T[][] {
  const chunks: T[][] = [];
  
  for (let i = 0; i < array.length; i += size) {
    chunks.push(array.slice(i, i + size));
  }
  
  return chunks;
}

/**
 * Sleep utility
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Format bytes
 */
export function formatBytes(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Debounce function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function (...args: Parameters<T>) {
    if (timeout) clearTimeout(timeout);
    
    timeout = setTimeout(() => {
      func(...args);
    }, wait);
  };
}

/**
 * Throttle function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false;

  return function (...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Example Usage:
 * 
 * // Measure performance
 * const users = await measurePerformance('getUsers', () => fetchUsers());
 * 
 * // Batch requests
 * const batcher = new RequestBatcher(async (ids) => fetchUsersByIds(ids));
 * const user1 = await batcher.request(1);
 * const user2 = await batcher.request(2);
 * 
 * // Rate limiting
 * const limiter = new RateLimiter(10, 1); // 10 requests per second
 * await limiter.consume();
 * await apiCall();
 * 
 * // Retry with backoff
 * const data = await retryWithBackoff(() => fetchData(), 3);
 * 
 * // Parallel with limit
 * const results = await parallelLimit(items, processItem, 5);
 */


































