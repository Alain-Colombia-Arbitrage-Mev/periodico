'use client';

import Image from 'next/image';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { useEffect, useState } from 'react';

interface Article {
  id: string;
  title: string;
  excerpt?: string;
  image_url: string;
  slug: string;
  category_slug: string;
  published_at: string;
  categorias?: {
    name: string;
    slug: string;
    color: string;
  };
}

interface SidebarProps {
  featuredArticle?: Article;
  sideArticles?: Article[];
  opinions?: Array<{
    id: string;
    title: string;
    author: string;
    slug: string;
    category_slug: string;
  }>;
}

export default function Sidebar({ featuredArticle, sideArticles, opinions }: SidebarProps) {
  const [recommendedArticles, setRecommendedArticles] = useState<Article[]>([]);
  const [isMobile, setIsMobile] = useState(true); // Default to mobile (hidden)

  useEffect(() => {
    // Check if we're on desktop
    const checkIfDesktop = () => {
      setIsMobile(window.innerWidth < 1024);
    };

    checkIfDesktop();
    window.addEventListener('resize', checkIfDesktop);

    return () => window.removeEventListener('resize', checkIfDesktop);
  }, []);

  useEffect(() => {
    // Only fetch if on desktop
    if (isMobile) return;

    async function fetchRecommended() {
      try {
        const res = await fetch('/api/noticias?limit=4');
        if (res.ok) {
          const data = await res.json();
          if (data.success && data.data) {
            setRecommendedArticles(data.data.slice(0, 4));
          }
        }
      } catch (error) {
        console.error('Error fetching recommended articles:', error);
      }
    }
    fetchRecommended();
  }, [isMobile]);

  // Don't render anything on mobile/tablet
  if (isMobile) {
    return null;
  }

  return (
    <aside className="w-[335px] space-y-6 sticky top-8">
      {/* Featured Article */}
      {featuredArticle && (
        <article className="border-b pb-6" style={{ borderColor: 'var(--nyt-border)' }}>
          <Link href={`/${featuredArticle.category_slug}/${featuredArticle.slug}`}>
            {featuredArticle.image_url ? (
              <div className="relative w-full h-[225px] mb-4 overflow-hidden rounded">
                <Image
                  src={featuredArticle.image_url}
                  alt={featuredArticle.title}
                  fill
                  className="object-cover hover:scale-105 transition-transform duration-300"
                  sizes="335px"
                  unoptimized
                />
              </div>
            ) : (
              <div className="relative w-full h-[225px] mb-4 bg-gray-200 flex items-center justify-center rounded">
                <span className="text-gray-400 text-xs">Sin imagen</span>
              </div>
            )}
          </Link>

          <Link href={`/${featuredArticle.category_slug}/${featuredArticle.slug}`}>
            <h3 className="text-[18px] font-bold mb-3 hover:underline transition line-clamp-3 leading-tight" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
              {featuredArticle.title}
            </h3>
          </Link>

          {featuredArticle.excerpt && (
            <p className="text-[14px] mb-3 line-clamp-3 leading-relaxed" style={{ color: 'var(--nyt-text-secondary)', fontFamily: 'var(--font-georgia)' }}>
              {featuredArticle.excerpt}
            </p>
          )}

          <p className="text-[10px]" style={{ color: 'var(--nyt-text-secondary)' }}>
            5 MIN READ
          </p>
        </article>
      )}

      {/* Side Articles Grid */}
      {sideArticles && sideArticles.length > 0 && (
        <div className="border-b pb-6" style={{ borderColor: 'var(--nyt-border)' }}>
          <div className="grid grid-cols-2 gap-4">
            {sideArticles.slice(0, 2).map((article) => (
              <Link
                key={article.id}
                href={`/${article.category_slug}/${article.slug}`}
                className="group"
              >
                {article.image_url ? (
                  <div className="relative w-full h-[100px] mb-2 overflow-hidden rounded">
                    <Image
                      src={article.image_url}
                      alt={article.title}
                      fill
                      className="object-cover group-hover:opacity-90 transition"
                      sizes="152px"
                      unoptimized
                    />
                  </div>
                ) : (
                  <div className="relative w-full h-[100px] mb-2 bg-gray-200 flex items-center justify-center rounded">
                    <span className="text-gray-400 text-xs">Sin imagen</span>
                  </div>
                )}
                <h4 className="text-[15px] font-bold line-clamp-3 group-hover:opacity-80 transition leading-snug" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                  {article.title}
                </h4>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Opinions Section */}
      {opinions && opinions.length > 0 && (
        <div className="space-y-4 pb-6 border-b" style={{ borderColor: 'var(--nyt-border)' }}>
          <h3 className="text-[16px] font-bold uppercase">Opinión</h3>

          {opinions.map((opinion) => (
            <article key={opinion.id} className="border-b border-gray-200 pb-4 last:border-0 last:pb-0">
              <Link href={`/${opinion.category_slug}/${opinion.slug}`}>
                <p className="text-[10px] uppercase mb-1" style={{ color: 'var(--nyt-text-gray)' }}>
                  {opinion.author}
                </p>
                <h4 className="text-[15px] font-bold hover:opacity-80 transition line-clamp-2 leading-snug" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                  {opinion.title}
                </h4>
              </Link>
            </article>
          ))}
        </div>
      )}

      {/* In Case You Missed It */}
      <div className="border-t pt-6 mt-6" style={{ borderColor: 'var(--nyt-border)' }}>
        <h3 className="text-[14px] font-bold mb-2 uppercase tracking-wide" style={{ fontFamily: 'var(--font-helvetica)', color: 'var(--nyt-text-primary)' }}>Más Leídas</h3>
        <p className="text-[11px] mb-5" style={{ color: 'var(--nyt-text-gray)', fontFamily: 'var(--font-helvetica)' }}>
          Las noticias más importantes del día
        </p>

        {/* Recommended articles */}
        {recommendedArticles.length > 0 && (
          <div className="space-y-5">
            {recommendedArticles.map((article: any) => {
              // Use categorias.slug if available, fallback to category_slug or 'politica'
              const categorySlug = article.categorias?.slug || article.category_slug || 'politica';
              return (
                <Link
                  key={article.id}
                  href={`/${categorySlug}/${article.slug}`}
                  className="block group"
                >
                  <article className="flex gap-3 pb-5 border-b border-gray-200 last:border-0 last:pb-0">
                    {article.image_url && (
                      <div className="relative w-20 h-20 flex-shrink-0 overflow-hidden rounded">
                        <Image
                          src={article.image_url}
                          alt={article.title}
                          fill
                          className="object-cover group-hover:opacity-90 transition"
                          sizes="80px"
                          unoptimized
                        />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <h4 className="text-[14px] font-bold line-clamp-3 group-hover:opacity-80 transition leading-snug mb-2" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                        {article.title}
                      </h4>
                      <p className="text-[10px]" style={{ color: 'var(--nyt-text-gray)' }}>
                        {formatDistanceToNow(new Date(article.published_at), {
                          addSuffix: true,
                          locale: es
                        })}
                      </p>
                    </div>
                  </article>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </aside>
  );
}

