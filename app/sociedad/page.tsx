'use client';

import { useEffect, useState } from 'react';
import { supabaseHelpers } from '@/lib/supabase';
import NYTHeader from '@/components/nyt/Header';
import MainHeadline from '@/components/nyt/MainHeadline';
import Sidebar from '@/components/nyt/Sidebar';
import Link from 'next/link';
import NewsImage from '@/components/NewsImage';
import { Users } from 'lucide-react';

interface Noticia {
  id: string;
  title: string;
  subtitle?: string;
  excerpt: string;
  content: string;
  image_url: string;
  slug: string;
  published_at: string;
  views: number;
  is_breaking: boolean;
  source_type: number;  // 0 = scraped, 1 = manual
  categorias: {
    name: string;
    slug: string;
    color: string;
  };
}

export default function SociedadPage() {
  const [noticias, setNoticias] = useState<Noticia[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchNoticias() {
      try {
        const { data, error } = await supabaseHelpers.getNoticias({
          status: 'published',
          category: 'sociedad',
          limit: 20
        });

        if (!error && data) {
          setNoticias(data as Noticia[]);
        }
      } catch (error) {
        console.error('Error loading noticias:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchNoticias();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--paper-bg)]">
        <NYTHeader />
        <div className="site-container flex items-center justify-center py-20">
          <p className="text-lg">Cargando noticias de sociedad...</p>
        </div>
        
      </div>
    );
  }

  const featuredNews = noticias[0];
  const recentNews = noticias.slice(1, 11);

  return (
    <div className="min-h-screen bg-[var(--paper-bg)]">
      <NYTHeader />

      <main className="site-container py-6 lg:py-8">
        {/* Category Header */}
        <div className="mb-6 lg:mb-8 pb-4 border-b border-[var(--border-soft)]">
          <div className="flex items-center gap-3 mb-2">
            <Users className="w-8 h-8" style={{ color: '#FF6B35' }} />
            <h1 className="text-3xl lg:text-4xl font-bold" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
              Sociedad
            </h1>
          </div>
          <p className="text-base lg:text-lg" style={{ color: 'var(--nyt-text-secondary)' }}>
            Noticias sobre educación, salud, cultura y la vida en sociedad
          </p>
        </div>

        {/* Main Content with Sidebar on Desktop */}
        <div className="flex gap-8">
          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Featured Article */}
            {featuredNews && (
              <div className="mb-8 lg:mb-12">
                <MainHeadline article={{
                  id: featuredNews.id,
                  title: featuredNews.title,
                  subtitle: featuredNews.subtitle,
                  excerpt: featuredNews.excerpt,
                  image_url: featuredNews.image_url,
                  slug: featuredNews.slug,
                  category_slug: 'sociedad',
                  published_at: featuredNews.published_at,
                  views: featuredNews.views
                }} />
              </div>
            )}

            {/* Recent News */}
            {recentNews.length > 0 ? (
              <div className="space-y-0">
                {recentNews.map((article) => (
                  <article key={article.id} className="mb-6 pb-6 lg:mb-8 lg:pb-8 border-b border-[var(--border-soft)]">
                    <div className="flex flex-col md:flex-row gap-4 md:gap-6">
                      <div className="flex-shrink-0 md:w-[280px] lg:w-[348px]">
                        <Link href={`/sociedad/${article.slug}`}>
                          <h2 className="text-lg md:text-[20px] font-bold mb-3 md:mb-4 hover:opacity-80 transition" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                            {article.title}
                          </h2>
                        </Link>
                        {article.excerpt && (
                          <p className="text-sm md:text-[16px] leading-relaxed line-clamp-3 md:line-clamp-4 mb-3" style={{ color: 'var(--nyt-text-secondary)', fontFamily: 'var(--font-georgia)' }}>
                            {article.excerpt}
                          </p>
                        )}
                      </div>
                      <div className="flex-shrink-0 flex-1 md:max-w-[420px] lg:max-w-[580px]">
                        <Link href={`/sociedad/${article.slug}`}>
                          {article.image_url ? (
                            <div className="relative w-full aspect-video md:aspect-auto md:h-[240px] lg:h-[300px] overflow-hidden rounded-sm bg-gray-100">
                              <NewsImage
                                src={article.image_url}
                                alt={article.title}
                                fill
                                className="object-contain hover:scale-105 transition-transform duration-300"
                                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 420px, 580px"
                                priority={false}
                              />
                            </div>
                          ) : (
                            <div className="relative w-full aspect-video md:aspect-auto md:h-[240px] lg:h-[300px] bg-gray-100 flex items-center justify-center rounded-sm">
                              <span className="text-gray-400 text-sm">Sin imagen</span>
                            </div>
                          )}
                        </Link>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="py-12 text-center">
                <p className="text-lg mb-2" style={{ color: 'var(--nyt-text-gray)' }}>
                  No hay noticias de sociedad disponibles
                </p>
                <Link href="/" className="text-sm hover:underline" style={{ color: '#0066FF' }}>
                  Volver al inicio
                </Link>
              </div>
            )}
          </div>

          {/* Sidebar - Hidden on Mobile */}
          <Sidebar />
        </div>
      </main>

      {/* Footer */}
      
    </div>
  );
}
