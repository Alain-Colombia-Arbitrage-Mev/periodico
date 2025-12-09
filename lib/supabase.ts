import { createClient } from '@supabase/supabase-js';

// Configuración de Supabase
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder-key';

// Solo crear el cliente si las variables están configuradas
const isConfigured = process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

export const supabase = isConfigured 
  ? createClient(supabaseUrl, supabaseAnonKey)
  : createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        persistSession: false,
        autoRefreshToken: false,
      },
    });

// Types para TypeScript
export interface Database {
  public: {
    Tables: {
      noticias: {
        Row: Noticia;
        Insert: Omit<Noticia, 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Omit<Noticia, 'id' | 'created_at' | 'updated_at'>>;
      };
      categorias: {
        Row: Categoria;
        Insert: Omit<Categoria, 'id' | 'created_at'>;
        Update: Partial<Omit<Categoria, 'id' | 'created_at'>>;
      };
      tags: {
        Row: Tag;
        Insert: Omit<Tag, 'id' | 'created_at'>;
        Update: Partial<Omit<Tag, 'id' | 'created_at'>>;
      };
      usuarios: {
        Row: Usuario;
        Insert: Omit<Usuario, 'id' | 'created_at' | 'updated_at'>;
        Update: Partial<Omit<Usuario, 'id' | 'created_at' | 'updated_at'>>;
      };
    };
  };
}

export interface Noticia {
  id: string;
  title: string;
  subtitle?: string;
  slug: string;
  category_id: string;
  excerpt: string;
  content: string;
  image_url: string;
  views: number;
  status: 'draft' | 'published' | 'archived';
  is_breaking: boolean;
  source_type: number;  // 0x00 (0) = scraper + LLM, 0x01 (1) = manual
  source_url?: string;
  published_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Categoria {
  id: string;
  name: string;
  slug: string;
  description?: string;
  color: string;
  icon?: string;
  order: number;
  created_at: string;
}

export interface Tag {
  id: string;
  name: string;
  slug: string;
  created_at: string;
}

export interface Usuario {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'editor' | 'author';
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface NoticiaTag {
  noticia_id: string;
  tag_id: string;
}

// Funciones helper para Supabase
export const supabaseHelpers = {
  // Noticias
  async getNoticias(filters?: {
    category?: string;  // Can be category UUID or category slug
    status?: string;
    source_type?: number;  // 0x00 (0) = scraper + LLM, 0x01 (1) = manual
    limit?: number;
    offset?: number;
    onlyRecent?: boolean;  // Filter only last 72 hours
    separateBySource?: boolean;  // If true, returns { manual: [], scraped: [] }
  }) {
    // Use inner join only if filtering by category, otherwise use left join
    const joinType = filters?.category ? 'categorias!inner(name, slug, color)' : 'categorias(name, slug, color)';

    let query = supabase
      .from('noticias')
      .select(`
        *,
        ${joinType}
      `)
      // Order by source_type DESC (1=manual first, 0=scraped second), then by date
      .order('source_type', { ascending: false })
      .order('published_at', { ascending: false, nullsFirst: false })
      .order('created_at', { ascending: false });

    // Filter only recent news (last 72 hours) only if explicitly requested
    if (filters?.onlyRecent === true) {
      const hoursAgo72 = new Date(Date.now() - 72 * 60 * 60 * 1000).toISOString();
      query = query.or(`published_at.gte.${hoursAgo72},created_at.gte.${hoursAgo72}`);
    }

    if (filters?.category) {
      // Filter by category slug using inner join
      query = query.eq('categorias.slug', filters.category);
    }

    if (filters?.status) {
      query = query.eq('status', filters.status);
    }

    if (filters?.source_type !== undefined) {
      query = query.eq('source_type', filters.source_type);
    }

    if (filters?.limit) {
      query = query.limit(filters.limit);
    }

    if (filters?.offset) {
      query = query.range(filters.offset, filters.offset + (filters.limit || 10) - 1);
    }

    return query;
  },

  async getNoticiaById(id: string) {
    return supabase
      .from('noticias')
      .select(`
        *,
        categorias(name, slug, color)
      `)
      .eq('id', id)
      .single();
  },

  async getNoticiaBySlug(slug: string) {
    return supabase
      .from('noticias')
      .select(`
        *,
        categorias(name, slug, color)
      `)
      .eq('slug', slug)
      .eq('status', 'published');
  },

  async createNoticia(noticia: Database['public']['Tables']['noticias']['Insert']) {
    return supabase
      .from('noticias')
      .insert(noticia)
      .select()
      .single();
  },

  async updateNoticia(id: string, updates: Database['public']['Tables']['noticias']['Update']) {
    return supabase
      .from('noticias')
      .update(updates)
      .eq('id', id)
      .select()
      .single();
  },

  async deleteNoticia(id: string) {
    return supabase
      .from('noticias')
      .delete()
      .eq('id', id);
  },

  async incrementViews(id: string) {
    // Usar RPC con SECURITY DEFINER para bypass RLS
    const { error } = await supabase.rpc('increment_views', { noticia_id: id });
    
    if (error) {
      // Fallback: intentar UPDATE directo si RPC falla
      console.warn('RPC increment_views failed, trying direct update:', error.message);
      
      const { data: current } = await supabase
        .from('noticias')
        .select('views')
        .eq('id', id)
        .single();
      
      const currentViews = current?.views || 0;
      
      return supabase
        .from('noticias')
        .update({ views: currentViews + 1 })
        .eq('id', id);
    }
    
    return { data: null, error: null };
  },

  // Categorías
  async getCategorias() {
    return supabase
      .from('categorias')
      .select('*')
      .order('order', { ascending: true });
  },

  // Tags
  async getTags() {
    return supabase
      .from('tags')
      .select('*')
      .order('name', { ascending: true });
  },

  async getNoticiasTags(noticiaId: string) {
    return supabase
      .from('noticias_tags')
      .select('tags(*)')
      .eq('noticia_id', noticiaId);
  },

  async getNoticiasByTag(tagName: string) {
    // Primero obtener el tag por nombre
    const { data: tag } = await supabase
      .from('tags')
      .select('id')
      .ilike('name', tagName)
      .single();

    if (!tag) {
      return { data: [], error: null };
    }

    // Luego obtener las noticias que tienen ese tag
    const { data: noticiasTags } = await supabase
      .from('noticias_tags')
      .select('noticia_id')
      .eq('tag_id', tag.id);

    if (!noticiasTags || noticiasTags.length === 0) {
      return { data: [], error: null };
    }

    const noticiaIds = noticiasTags.map(nt => nt.noticia_id);

    // Obtener las noticias completas
    return supabase
      .from('noticias')
      .select(`
        *,
        categorias(name, slug, color)
      `)
      .in('id', noticiaIds)
      .eq('status', 'published')
      .order('published_at', { ascending: false, nullsFirst: false });
  },

  /**
   * Get noticias separated by source type for dual grid layout
   * Returns: { manual: Noticia[], scraped: Noticia[] }
   */
  async getNoticiasSeparated(filters?: {
    category?: string;
    status?: string;
    limit?: number;
  }) {
    const joinType = filters?.category ? 'categorias!inner(name, slug, color)' : 'categorias(name, slug, color)';

    // Get manual noticias (source_type = 1)
    let manualQuery = supabase
      .from('noticias')
      .select(`*, ${joinType}`)
      .eq('source_type', 1)
      .order('published_at', { ascending: false, nullsFirst: false });

    // Get scraped noticias (source_type = 0)
    let scrapedQuery = supabase
      .from('noticias')
      .select(`*, ${joinType}`)
      .eq('source_type', 0)
      .order('published_at', { ascending: false, nullsFirst: false });

    if (filters?.category) {
      manualQuery = manualQuery.eq('categorias.slug', filters.category);
      scrapedQuery = scrapedQuery.eq('categorias.slug', filters.category);
    }

    if (filters?.status) {
      manualQuery = manualQuery.eq('status', filters.status);
      scrapedQuery = scrapedQuery.eq('status', filters.status);
    }

    if (filters?.limit) {
      manualQuery = manualQuery.limit(filters.limit);
      scrapedQuery = scrapedQuery.limit(filters.limit);
    }

    const [manualResult, scrapedResult] = await Promise.all([
      manualQuery,
      scrapedQuery
    ]);

    return {
      manual: manualResult.data || [],
      scraped: scrapedResult.data || [],
      error: manualResult.error || scrapedResult.error
    };
  },
};

