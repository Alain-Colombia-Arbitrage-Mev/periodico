/**
 * NOTICIA SERVICE - BUSINESS LOGIC LAYER
 * Serverless-optimized with caching and error handling
 */

import { noticiaRepo, cache, type Noticia } from '../database';

// ============================================
// SERVICE LAYER - BUSINESS LOGIC
// ============================================
export class NoticiaService {
  private static instance: NoticiaService;

  private constructor() {}

  static getInstance(): NoticiaService {
    if (!NoticiaService.instance) {
      NoticiaService.instance = new NoticiaService();
    }
    return NoticiaService.instance;
  }

  // ============================================
  // GET METHODS
  // ============================================
  
  async getAllNoticias(options?: {
    category?: string;
    page?: number;
    limit?: number;
  }): Promise<{ data: Noticia[]; total: number; page: number; totalPages: number }> {
    try {
      const page = options?.page || 1;
      const limit = options?.limit || 20;
      const offset = (page - 1) * limit;

      const data = await noticiaRepo.findAll({
        category: options?.category,
        limit,
        offset,
      });

      // Get total count (cached)
      const cacheKey = `count:noticias:${options?.category || 'all'}`;
      let total = cache.get(cacheKey);
      
      if (!total) {
        // Simulate count - in production, use actual count query
        total = 150; // Replace with actual count
        cache.set(cacheKey, total, 600000); // 10 min cache
      }

      return {
        data,
        total,
        page,
        totalPages: Math.ceil(total / limit),
      };
    } catch (error) {
      console.error('Error in getAllNoticias:', error);
      throw new Error('Failed to fetch noticias');
    }
  }

  async getNoticiaById(id: string): Promise<Noticia | null> {
    try {
      const noticia = await noticiaRepo.findById(id);
      
      if (noticia) {
        // Increment views asynchronously
        this.incrementViewsAsync(id);
      }

      return noticia;
    } catch (error) {
      console.error('Error in getNoticiaById:', error);
      return null;
    }
  }

  async getBreakingNews(): Promise<Noticia[]> {
    try {
      return await noticiaRepo.findBreaking();
    } catch (error) {
      console.error('Error in getBreakingNews:', error);
      return [];
    }
  }

  async getNoticiasByCategory(category: string, limit = 20): Promise<Noticia[]> {
    try {
      const result = await this.getAllNoticias({ category, limit });
      return result.data;
    } catch (error) {
      console.error('Error in getNoticiasByCategory:', error);
      return [];
    }
  }

  async getFeaturedNoticias(limit = 5): Promise<Noticia[]> {
    try {
      const cacheKey = `noticias:featured:${limit}`;
      const cached = cache.get(cacheKey);
      if (cached) return cached;

      // In production, filter by is_featured flag
      const result = await this.getAllNoticias({ limit });
      const featured = result.data.slice(0, limit);

      cache.set(cacheKey, featured, 300000); // 5 min cache
      return featured;
    } catch (error) {
      console.error('Error in getFeaturedNoticias:', error);
      return [];
    }
  }

  // ============================================
  // WRITE METHODS
  // ============================================

  async createNoticia(data: Partial<Noticia>): Promise<Noticia> {
    try {
      // Validate required fields
      if (!data.title || !data.category || !data.excerpt) {
        throw new Error('Missing required fields');
      }

      // Set defaults
      const noticiaData: any = {
        ...data,
        status: data.status || 'draft',
        views: 0,
        source_type: (data as any).source_type ?? 1, // Default to manual (1)
        published_at: data.published_at || new Date().toISOString(),
      };

      const noticia = await noticiaRepo.create(noticiaData);

      // Invalidate relevant caches
      this.invalidateCache();

      return noticia;
    } catch (error) {
      console.error('Error in createNoticia:', error);
      throw new Error('Failed to create noticia');
    }
  }

  async updateNoticia(id: string, data: Partial<Noticia>): Promise<Noticia> {
    try {
      const noticia = await noticiaRepo.update(id, data);
      
      // Invalidate relevant caches
      this.invalidateCache();

      return noticia;
    } catch (error) {
      console.error('Error in updateNoticia:', error);
      throw new Error('Failed to update noticia');
    }
  }

  async deleteNoticia(id: string): Promise<void> {
    try {
      await noticiaRepo.delete(id);
      
      // Invalidate relevant caches
      this.invalidateCache();
    } catch (error) {
      console.error('Error in deleteNoticia:', error);
      throw new Error('Failed to delete noticia');
    }
  }

  // ============================================
  // UTILITY METHODS
  // ============================================

  private async incrementViewsAsync(id: string): Promise<void> {
    try {
      // Use setTimeout to make it truly async and non-blocking
      setTimeout(async () => {
        await noticiaRepo.incrementViews(id);
      }, 0);
    } catch (error) {
      // Silent fail - views are not critical
      console.error('Error incrementing views:', error);
    }
  }

  private invalidateCache(): void {
    // Clear all noticia-related caches
    cache.clear();
  }

  // ============================================
  // ANALYTICS & STATS
  // ============================================

  async getStats(): Promise<{
    total: number;
    byCategory: Record<string, number>;
    trending: Noticia[];
  }> {
    try {
      const cacheKey = 'stats:noticias';
      const cached = cache.get(cacheKey);
      if (cached) return cached;

      const allNoticias = await this.getAllNoticias({ limit: 1000 });
      
      const byCategory: Record<string, number> = {};
      for (const noticia of allNoticias.data) {
        byCategory[noticia.category] = (byCategory[noticia.category] || 0) + 1;
      }

      const trending = allNoticias.data
        .sort((a, b) => b.views - a.views)
        .slice(0, 10);

      const stats = {
        total: allNoticias.total,
        byCategory,
        trending,
      };

      cache.set(cacheKey, stats, 600000); // 10 min cache
      return stats;
    } catch (error) {
      console.error('Error in getStats:', error);
      return {
        total: 0,
        byCategory: {},
        trending: [],
      };
    }
  }
}

// ============================================
// EXPORT SINGLETON
// ============================================
export const noticiaService = NoticiaService.getInstance();

