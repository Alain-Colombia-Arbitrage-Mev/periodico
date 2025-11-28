/**
 * Custom hooks optimizados para fetching de noticias usando SWR
 */
import useSWR from 'swr';
import { supabaseHelpers } from '@/lib/supabase';

// Fetcher function para SWR
const fetcher = async (key: string) => {
  const params = new URLSearchParams(key.split('?')[1] || '');
  const filters: any = {
    status: params.get('status') || 'published',
  };

  if (params.get('category')) filters.category = params.get('category');
  if (params.get('limit')) filters.limit = parseInt(params.get('limit') || '10');
  if (params.get('offset')) filters.offset = parseInt(params.get('offset') || '0');
  if (params.get('onlyRecent') === 'true') filters.onlyRecent = true;

  const { data, error } = await supabaseHelpers.getNoticias(filters);
  
  if (error) throw error;
  return data || [];
};

/**
 * Hook para obtener noticias con caching y revalidación automática
 */
export function useNoticias(filters?: {
  category?: string;
  status?: string;
  limit?: number;
  offset?: number;
  onlyRecent?: boolean;
}) {
  // Construir key para SWR
  const params = new URLSearchParams();
  if (filters?.status) params.set('status', filters.status);
  if (filters?.category) params.set('category', filters.category);
  if (filters?.limit) params.set('limit', filters.limit.toString());
  if (filters?.offset) params.set('offset', filters.offset.toString());
  if (filters?.onlyRecent) params.set('onlyRecent', 'true');

  const key = `noticias?${params.toString()}`;

  const { data, error, isLoading, isValidating, mutate } = useSWR(
    key,
    fetcher,
    {
      // Revalidar cada 60 segundos
      refreshInterval: 60000,
      // Revalidar cuando la ventana recupera el foco
      revalidateOnFocus: true,
      // Revalidar cuando se reconecta
      revalidateOnReconnect: true,
      // Mantener datos anteriores mientras se cargan nuevos (SWR v2 usa keepPreviousData)
      keepPreviousData: true,
      // Tiempo de deduplicación (evitar múltiples requests simultáneos)
      dedupingInterval: 2000,
      // Error retry
      errorRetryCount: 3,
      errorRetryInterval: 5000,
      // No revalidar si los datos no están stale
      revalidateIfStale: true,
    }
  );

  return {
    noticias: data || [],
    isLoading,
    isValidating,
    error,
    mutate, // Para revalidar manualmente
  };
}

/**
 * Hook para obtener una noticia principal (más reciente)
 */
export function useMainArticle() {
  return useNoticias({ status: 'published', limit: 1 });
}

/**
 * Hook para obtener noticias breaking
 */
export function useBreakingNews() {
  const { noticias, ...rest } = useNoticias({ status: 'published', limit: 20 });
  const breaking = noticias.filter((n: any) => n.is_breaking).slice(0, 3);
  return { breakingNews: breaking, ...rest };
}

/**
 * Hook para obtener noticias recientes
 */
export function useRecentNews(limit: number = 20) {
  const { noticias, ...rest } = useNoticias({ status: 'published', limit });
  // Excluir la primera (que es la principal)
  const recent = noticias.slice(1, limit + 1);
  return { recentNews: recent, ...rest };
}

/**
 * Hook para obtener noticias por categoría
 */
export function useNoticiasByCategory(category: string, limit: number = 20) {
  return useNoticias({ category, status: 'published', limit });
}

/**
 * Hook para obtener noticias separadas por tipo de fuente
 * Returns: { manualNews, scrapedNews, isLoading, error }
 */
export function useNoticiasSeparated(filters?: {
  category?: string;
  limit?: number;
}) {
  const { noticias, isLoading, error, mutate } = useNoticias({
    status: 'published',
    category: filters?.category,
    limit: filters?.limit || 20
  });

  // Separate by source_type: 1 = manual, 0 = scraped
  const manualNews = noticias.filter((n: any) => n.source_type === 1);
  const scrapedNews = noticias.filter((n: any) => n.source_type === 0);

  return {
    manualNews,
    scrapedNews,
    allNews: noticias,
    isLoading,
    error,
    mutate
  };
}

