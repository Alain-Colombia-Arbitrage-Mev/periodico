'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Eye } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import NewsImage from './NewsImage';

interface Noticia {
  id: string;
  title: string;
  subtitle?: string;
  slug: string;
  category: string;
  category_slug: string;
  excerpt: string;
  content: string;
  image_url: string;
  author: string;
  views: number;
  is_breaking: boolean;
  source_type: number;
  source_url?: string;
  published_at: string;
  created_at: string;
}

interface NoticiasGridProps {
  category?: string;
  limit?: number;
  className?: string;
}

function getCategoryClass(slug: string) {
  const classes: Record<string, string> = {
    politica: 'category-politica',
    economia: 'category-economia',
    judicial: 'category-judicial',
    internacional: 'category-internacional',
    sociedad: 'category-sociedad',
  };
  return classes[slug] || 'bg-gray-600 text-white';
}

export default function NoticiasGrid({ category, limit = 12, className = '' }: NoticiasGridProps) {
  const [noticias, setNoticias] = useState<Noticia[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchNoticias() {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          status: 'published',
          limit: limit.toString(),
          ...(category && { category }),
        });

        const response = await fetch(`/api/noticias?${params}`);
        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || 'Error al cargar noticias');
        }

        setNoticias(result.data || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    }

    fetchNoticias();
  }, [category, limit]);

  if (loading) {
    return (
      <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`}>
        {[...Array(6)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-gray-200 aspect-video rounded-t-lg"></div>
            <div className="p-4 space-y-3 bg-white rounded-b-lg">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              <div className="h-3 bg-gray-200 rounded w-4/6"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 bg-red-50 border border-red-200 rounded-lg ${className}`}>
        <p className="text-red-600">Error: {error}</p>
      </div>
    );
  }

  if (noticias.length === 0) {
    return (
      <div className={`p-8 text-center text-gray-500 ${className}`}>
        <p>No hay noticias disponibles en este momento.</p>
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`}>
      {noticias.map((noticia) => (
        <article key={noticia.id} className="ln-card group cursor-pointer overflow-hidden">
          <Link href={`/${noticia.category_slug}/${noticia.slug}`}>
            <div className="relative aspect-video overflow-hidden">
              <NewsImage
                src={noticia.image_url}
                alt={noticia.title}
                fill
                className="object-cover transition-transform duration-300 group-hover:scale-105"
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                priority={false}
              />
              <div className="absolute top-3 left-3 flex gap-2 flex-wrap">
                <span className={`category-badge ${getCategoryClass(noticia.category_slug)}`}>
                  {noticia.category}
                </span>
                {noticia.source_type === 0 && (
                  <span className="category-badge bg-purple-600 text-white text-xs">
                    Auto
                  </span>
                )}
                {noticia.is_breaking && (
                  <span className="category-badge bg-red-600 text-white animate-pulse">
                    URGENTE
                  </span>
                )}
              </div>
            </div>
            <div className="p-4 space-y-2">
              <h3 className="article-title text-base lg:text-lg group-hover:text-blue-600 transition-colors line-clamp-3 leading-tight">
                {noticia.title}
              </h3>
              {noticia.subtitle && (
                <p className="text-sm font-medium text-gray-600 line-clamp-1">
                  {noticia.subtitle}
                </p>
              )}
              <p className="article-excerpt line-clamp-2 text-sm leading-relaxed">
                {noticia.excerpt}
              </p>
              <div className="article-meta text-xs pt-2 flex-wrap" style={{borderTop: '1px solid var(--ln-neutral-200)'}}>
                <time style={{color: 'var(--ln-neutral-400)'}}>
                  {formatDistanceToNow(new Date(noticia.published_at), {
                    addSuffix: true,
                    locale: es
                  })}
                </time>
                <span className="hidden sm:inline">•</span>
                <span className="flex items-center gap-1 sm:inline-flex" style={{color: 'var(--ln-neutral-400)'}}>
                  <Eye className="w-3 h-3" />
                  {noticia.views.toLocaleString()}
                </span>
                <span className="hidden md:inline">•</span>
                <span className="hidden md:inline" style={{color: 'var(--ln-neutral-400)'}}>{noticia.author}</span>
              </div>
            </div>
          </Link>
        </article>
      ))}
    </div>
  );
}
