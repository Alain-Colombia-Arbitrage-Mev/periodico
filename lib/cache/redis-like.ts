/**
 * PRODUCTION-GRADE IN-MEMORY CACHE
 * Thread-safe, LRU eviction, TTL support
 */

interface CacheEntry<T> {
  value: T;
  expiry: number;
  lastAccess: number;
}

export class ProductionCache {
  private cache: Map<string, CacheEntry<any>>;
  private maxSize: number;
  private readonly DEFAULT_TTL = 300000; // 5 minutes

  constructor(maxSize = 1000) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }

  /**
   * Get value from cache with automatic expiry check
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    // Check expiry
    if (Date.now() > entry.expiry) {
      this.cache.delete(key);
      return null;
    }

    // Update last access for LRU
    entry.lastAccess = Date.now();
    return entry.value as T;
  }

  /**
   * Set value in cache with optional TTL
   */
  set<T>(key: string, value: T, ttl = this.DEFAULT_TTL): void {
    // Evict if cache is full
    if (this.cache.size >= this.maxSize) {
      this.evictLRU();
    }

    this.cache.set(key, {
      value,
      expiry: Date.now() + ttl,
      lastAccess: Date.now(),
    });
  }

  /**
   * Delete specific key
   */
  delete(key: string): void {
    this.cache.delete(key);
  }

  /**
   * Clear all cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cache size
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * Evict least recently used item
   */
  private evictLRU(): void {
    let oldestKey: string | null = null;
    let oldestTime = Infinity;

    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccess < oldestTime) {
        oldestTime = entry.lastAccess;
        oldestKey = key;
      }
    }

    if (oldestKey) {
      this.cache.delete(oldestKey);
    }
  }

  /**
   * Clean expired entries (call periodically)
   */
  cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiry) {
        this.cache.delete(key);
      }
    }
  }

  /**
   * Get cache statistics
   */
  stats(): { size: number; maxSize: number; utilization: number } {
    return {
      size: this.cache.size,
      maxSize: this.maxSize,
      utilization: (this.cache.size / this.maxSize) * 100,
    };
  }
}

// Singleton instance
export const productionCache = new ProductionCache(2000);

// Cleanup expired entries every 5 minutes
if (typeof window === 'undefined') {
  setInterval(() => {
    productionCache.cleanup();
  }, 300000);
}
