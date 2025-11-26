/**
 * IMAGE OPTIMIZATION UTILITIES
 * Handles responsive images, lazy loading, and CDN optimization
 */

export interface ImageConfig {
  src: string;
  width?: number;
  height?: number;
  quality?: number;
  blur?: boolean;
}

/**
 * Generate optimized Supabase image URL with transformations
 */
export function getOptimizedImageUrl(
  url: string,
  options: {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'webp' | 'avif' | 'jpg';
  } = {}
): string {
  // If already a Supabase URL, can add transform parameters
  if (url.includes('dnacsmoubqrzpbvjhary.supabase.co')) {
    const params = new URLSearchParams();

    if (options.width) params.set('width', options.width.toString());
    if (options.height) params.set('height', options.height.toString());
    if (options.quality) params.set('quality', options.quality.toString());
    if (options.format) params.set('format', options.format);

    const queryString = params.toString();
    return queryString ? `${url}?${queryString}` : url;
  }

  return url;
}

/**
 * Generate srcSet for responsive images
 */
export function generateSrcSet(
  baseUrl: string,
  sizes: number[] = [640, 750, 828, 1080, 1200, 1920]
): string {
  return sizes
    .map(size => `${getOptimizedImageUrl(baseUrl, { width: size })} ${size}w`)
    .join(', ');
}

/**
 * Get blur placeholder for progressive image loading
 */
export function getBlurDataURL(): string {
  return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iODAwIiBoZWlnaHQ9IjQwMCIgZmlsbD0iI2U1ZTdlYiIvPjwvc3ZnPg==';
}

/**
 * Validate image URL and return fallback if invalid
 */
export function validateImageUrl(url: string | null | undefined): string {
  if (!url || url.trim() === '' || url.includes('data:image/svg+xml')) {
    return getBlurDataURL();
  }

  // Remove malformed data URIs
  if (url.includes('dnacsmoubqrzpbvjhary.supabase.co/storage/v1/object/public/noticias/data:')) {
    return getBlurDataURL();
  }

  return url;
}

/**
 * Preload critical images
 */
export function preloadImage(url: string): void {
  if (typeof window === 'undefined') return;

  const link = document.createElement('link');
  link.rel = 'preload';
  link.as = 'image';
  link.href = url;
  document.head.appendChild(link);
}

/**
 * Check if image URL is from Supabase Storage
 */
export function isSupabaseImage(url: string): boolean {
  return url.includes('dnacsmoubqrzpbvjhary.supabase.co');
}
