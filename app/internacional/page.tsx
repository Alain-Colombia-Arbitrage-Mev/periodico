'use client';

import { useEffect, useState } from 'react';
import { supabaseHelpers } from '@/lib/supabase';
import NYTHeader from '@/components/nyt/Header';
import MainHeadline from '@/components/nyt/MainHeadline';
import Sidebar from '@/components/nyt/Sidebar';
import Link from 'next/link';
import NewsImage from '@/components/NewsImage';
import { Globe2, Pen, Bot } from 'lucide-react';

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

export default function InternacionalPage() {
  const [noticias, setNoticias] = useState<Noticia[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchNoticias() {
      try {
        const { data, error } = await supabaseHelpers.getNoticias({
          status: 'published',
          category: 'internacional',
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
      <div className="min-h-screen bg-white">
        <NYTHeader />
        <div className="flex items-center justify-center py-20">
          <p className="text-lg">Cargando noticias internacionales...</p>
        </div>
        
      </div>
    );
  }

  const featuredNews = noticias[0];
  const recentNews = noticias.slice(1, 11);
  const sidebarNews = noticias.slice(1, 5);

  return (
    <div className="min-h-screen bg-white">
      <NYTHeader />

      <main className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-10 py-6 lg:py-8">
        {/* Category Header */}
        <div className="mb-6 lg:mb-8 pb-4 border-b-2 border-black">
          <div className="flex items-center gap-3 mb-2">
            <Globe2 className="w-8 h-8" style={{ color: '#4169E1' }} />
            <h1 className="text-3xl lg:text-4xl font-bold" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
              Internacional
            </h1>
          </div>
          <p className="text-base lg:text-lg" style={{ color: 'var(--nyt-text-secondary)' }}>
            Noticias internacionales y cobertura de eventos mundiales
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
          {/* Main Content */}
          <div className="lg:col-span-8 max-w-full lg:max-w-[976px]">
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
                  category_slug: 'internacional',
                  published_at: featuredNews.published_at,
                  views: featuredNews.views
                }} />
              </div>
            )}

            {/* Recent News */}
            {recentNews.length > 0 ? (
              <div className="space-y-0">
                {recentNews.map((article) => (
                  <article key={article.id} className="mb-6 pb-6 lg:mb-8 lg:pb-8 border-b border-black">
                    <div className="flex flex-col md:flex-row gap-4 md:gap-6">
                      <div className="flex-shrink-0 md:w-[280px] lg:w-[348px]">
                        {/* Source type badge */}
                        <div className="mb-2">
                          {article.source_type === 1 ? (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-600 text-white text-xs font-medium rounded">
                              <Pen className="w-3 h-3" />
                              Editorial
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-600 text-white text-xs font-medium rounded">
                              <Bot className="w-3 h-3" />
                              Auto
                            </span>
                          )}
                        </div>
                        <Link href={`/internacional/${article.slug}`}>
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
                        <Link href={`/internacional/${article.slug}`}>
                          {article.image_url ? (
                            <div className="relative w-full aspect-video md:aspect-auto md:h-[240px] lg:h-[300px] overflow-hidden rounded-sm">
                              <NewsImage
                                src={article.image_url}
                                alt={article.title}
                                fill
                                className="object-cover hover:scale-105 transition-transform duration-300"
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
                  No hay noticias internacionales disponibles
                </p>
                <Link href="/" className="text-sm hover:underline" style={{ color: '#0066FF' }}>
                  Volver al inicio
                </Link>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="hidden lg:block lg:col-span-4 lg:max-w-[335px] lg:ml-auto">
            <Sidebar
              featuredArticle={sidebarNews[0] ? {
                id: sidebarNews[0].id,
                title: sidebarNews[0].title,
                excerpt: sidebarNews[0].excerpt,
                image_url: sidebarNews[0].image_url,
                slug: sidebarNews[0].slug,
                category_slug: 'internacional',
                published_at: sidebarNews[0].published_at
              } : undefined}
              sideArticles={sidebarNews.slice(1).map(a => ({
                id: a.id,
                title: a.title,
                image_url: a.image_url,
                slug: a.slug,
                category_slug: 'internacional',
                published_at: a.published_at
              }))}
            />
          </div>
        </div>
      </main>

      {/* Bloomberg Footer */}
      
    </div>
  );
}
