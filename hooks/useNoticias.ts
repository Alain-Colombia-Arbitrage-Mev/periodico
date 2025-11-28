/**
 * OPTIMIZED NEWS FETCHING HOOK
 * Implements SWR pattern with caching, deduplication, and automatic revalidation
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface UseNoticiasOptions {
  category?: string;
  limit?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface NoticiasState<T> {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
  mutate: () => Promise<void>;
}

// In-memory cache to deduplicate requests
const requestCache = new Map<string, Promise<any>>();
const dataCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 60000; // 1 minute

/**
 * Optimized hook for fetching noticias with caching and deduplication
 */
export function useNoticias<T = any>(
  endpoint: string,
  options: UseNoticiasOptions = {}
): NoticiasState<T> {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const { autoRefresh = false, refreshInterval = 30000 } = options;
  const isMounted = useRef(true);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const cacheKey = `${endpoint}:${JSON.stringify(options)}`;

  const fetchData = useCallback(async (force = false) => {
    try {
      if (!force) {
        const cached = dataCache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
          if (isMounted.current) {
            setData(cached.data);
            setIsLoading(false);
          }
          return;
        }
      }

      let request = requestCache.get(cacheKey);

      if (!request) {
        const params = new URLSearchParams();
        if (options.category) params.set('category', options.category);
        if (options.limit) params.set('limit', options.limit.toString());
        const url = params.toString() ? `${endpoint}?${params}` : endpoint;

        request = fetch(url, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          cache: 'force-cache',
          next: { revalidate: 60 },
        }).then(async (res) => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          return res.json();
        });

        requestCache.set(cacheKey, request);
        request.finally(() => requestCache.delete(cacheKey));
      }

      const result = await request;
      dataCache.set(cacheKey, { data: result, timestamp: Date.now() });

      if (isMounted.current) {
        setData(result);
        setError(null);
        setIsLoading(false);
      }
    } catch (err) {
      if (isMounted.current) {
        setError(err as Error);
        setIsLoading(false);
      }
    }
  }, [cacheKey, endpoint, options.category, options.limit]);

  const mutate = useCallback(async () => {
    setIsLoading(true);
    await fetchData(true);
  }, [fetchData]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(() => fetchData(true), refreshInterval);
      return () => {
        if (intervalRef.current) clearInterval(intervalRef.current);
      };
    }
  }, [autoRefresh, refreshInterval, fetchData]);

  useEffect(() => {
    return () => {
      isMounted.current = false;
    };
  }, []);

  return { data, isLoading, error, mutate };
}

export function useNoticia(slug: string) {
  return useNoticias(`/api/noticias/${slug}`);
}

export function useNoticiasByCategory(category: string, limit = 20) {
  return useNoticias('/api/noticias', { category, limit });
}

export function useBreakingNews() {
  return useNoticias('/api/noticias?breaking=true', { autoRefresh: true, refreshInterval: 30000 });
}
