/**
 * Server-side Caching System
 * In-memory cache với TTL (Time To Live)
 */

interface CacheItem<T> {
  value: T;
  expiry: number;
  createdAt: number;
}

class Cache {
  private store = new Map<string, CacheItem<any>>();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  /**
   * Get value from cache
   */
  get<T>(key: string): T | null {
    const item = this.store.get(key);

    if (!item) {
      return null;
    }

    // Check if expired
    if (Date.now() > item.expiry) {
      this.store.delete(key);
      return null;
    }

    return item.value as T;
  }

  /**
   * Set value in cache
   */
  set<T>(key: string, value: T, ttl: number = this.defaultTTL): void {
    const item: CacheItem<T> = {
      value,
      expiry: Date.now() + ttl,
      createdAt: Date.now(),
    };

    this.store.set(key, item);
  }

  /**
   * Delete value from cache
   */
  delete(key: string): boolean {
    return this.store.delete(key);
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.store.clear();
  }

  /**
   * Get all keys
   */
  keys(): string[] {
    return Array.from(this.store.keys());
  }

  /**
   * Check if key exists and not expired
   */
  has(key: string): boolean {
    return this.get(key) !== null;
  }

  /**
   * Get or set pattern (memoization)
   */
  async getOrSet<T>(
    key: string,
    factory: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    const cached = this.get<T>(key);
    
    if (cached !== null) {
      return cached;
    }

    const value = await factory();
    this.set(key, value, ttl);
    return value;
  }

  /**
   * Clean up expired items
   */
  cleanup(): void {
    const now = Date.now();
    
    for (const [key, item] of this.store.entries()) {
      if (now > item.expiry) {
        this.store.delete(key);
      }
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    const items = Array.from(this.store.values());
    const now = Date.now();
    
    return {
      size: this.store.size,
      expired: items.filter(item => now > item.expiry).length,
      valid: items.filter(item => now <= item.expiry).length,
      oldestItem: items.length > 0 ? 
        Math.min(...items.map(item => item.createdAt)) : null,
    };
  }
}

// Singleton instance
const cache = new Cache();

// Auto cleanup every 10 minutes
if (typeof setInterval !== 'undefined') {
  setInterval(() => {
    cache.cleanup();
  }, 10 * 60 * 1000);
}

export default cache;

/**
 * Helper: Generate cache key from parameters
 */
export function generateCacheKey(prefix: string, ...params: any[]): string {
  return `${prefix}:${params.map(p => JSON.stringify(p)).join(':')}`;
}

/**
 * Helper: Memoize function with cache
 */
export function memoize<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  keyGenerator: (...args: Parameters<T>) => string,
  ttl?: number
): T {
  return (async (...args: Parameters<T>) => {
    const key = keyGenerator(...args);
    return cache.getOrSet(key, () => fn(...args), ttl);
  }) as T;
}

/**
 * Cache decorator (for class methods)
 */
export function Cached(ttl?: number) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const key = `${target.constructor.name}:${propertyKey}:${JSON.stringify(args)}`;
      return cache.getOrSet(key, () => originalMethod.apply(this, args), ttl);
    };

    return descriptor;
  };
}

/**
 * Example Usage:
 * 
 * // Simple get/set
 * cache.set('users', users, 60000); // 1 minute
 * const users = cache.get<User[]>('users');
 * 
 * // Get or set pattern
 * const users = await cache.getOrSet('users', async () => {
 *   return await fetchUsersFromDB();
 * }, 60000);
 * 
 * // Memoize function
 * const getUsers = memoize(
 *   async (id: number) => fetchUser(id),
 *   (id) => `user:${id}`,
 *   60000
 * );
 */

















