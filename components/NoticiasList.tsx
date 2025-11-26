'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Eye } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface Noticia {
  id: string;
  title: string;
  subtitle?: string;
  slug: string;
  category: string;
  category_slug: string;
  excerpt: string;
  image_url: string;
  author: string;
  views: number;
  is_breaking: boolean;
  source_type: number;
  published_at: string;
}

interface NoticiasListProps {
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

export default function NoticiasList({ category, limit = 8, className = '' }: NoticiasListProps) {
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
      <div className={`space-y-0 bg-white border border-gray-200 ${className}`}>
        {[...Array(4)].map((_, i) => (
          <div key={i} className="p-4 flex gap-4 border-b border-gray-200 last:border-0 animate-pulse">
            <div className="w-40 h-24 bg-gray-200 rounded flex-shrink-0"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-full"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
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
      <div className={`p-8 text-center text-gray-500 bg-white border border-gray-200 rounded-lg ${className}`}>
        <p>No hay noticias disponibles.</p>
      </div>
    );
  }

  return (
    <div className={`space-y-0 bg-white border border-gray-200 ${className}`}>
      {noticias.map((noticia, index) => (
        <article
          key={noticia.id}
          className="ln-card-horizontal ln-card-md group cursor-pointer"
          style={{
            borderBottom: index < noticias.length - 1 ? '1px solid var(--ln-neutral-200)' : 'none'
          }}
        >
          <Link href={`/${noticia.category_slug}/${noticia.slug}`} className="flex gap-4 w-full">
            <div className="ln-card-image">
              <Image
                src={noticia.image_url}
                alt={noticia.title}
                fill
                className="object-cover group-hover:scale-105 transition-transform duration-300"
                sizes="160px"
              />
              <div className="absolute bottom-2 left-2 flex gap-1">
                <span className={`category-badge text-xs px-2 py-0.5 ${getCategoryClass(noticia.category_slug)}`}>
                  {noticia.category}
                </span>
                {noticia.is_breaking && (
                  <span className="category-badge text-xs px-2 py-0.5 bg-red-600 text-white animate-pulse">
                    URGENTE
                  </span>
                )}
              </div>
            </div>
            <div className="flex-1 space-y-2">
              <h4 className="font-serif text-lg font-bold group-hover:text-blue-600 transition-colors line-clamp-2" style={{color: 'var(--ln-neutral-800)'}}>
                {noticia.title}
              </h4>
              <p className="text-sm line-clamp-2" style={{color: 'var(--ln-neutral-600)'}}>
                {noticia.excerpt}
              </p>
              <div className="article-meta text-xs">
                <time style={{color: 'var(--ln-neutral-400)'}}>
                  {formatDistanceToNow(new Date(noticia.published_at), {
                    addSuffix: true,
                    locale: es
                  })}
                </time>
                <span>•</span>
                <span className="flex items-center gap-1" style={{color: 'var(--ln-neutral-400)'}}>
                  <Eye className="w-3 h-3" />
                  {noticia.views.toLocaleString()}
                </span>
                <span>•</span>
                <span style={{color: 'var(--ln-neutral-400)'}}>{noticia.author}</span>
              </div>
            </div>
          </Link>
        </article>
      ))}
    </div>
  );
}
