'use client';

import { useMainArticle, useBreakingNews, useRecentNews } from '@/lib/hooks/useNoticias';
import NYTHeader from '@/components/nyt/Header';
import MainHeadline from '@/components/nyt/MainHeadline';
import LiveSection from '@/components/nyt/LiveSection';
import Sidebar from '@/components/nyt/Sidebar';
import Link from 'next/link';
import NewsImage from '@/components/NewsImage';
import { SkeletonPage } from '@/components/SkeletonLoaders';

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
  source_type: number;  // 0x00 (0) = scraper + LLM, 0x01 (1) = manual
  source_url?: string;
  categorias: {
    name: string;
    slug: string;
    color: string;
  };
  usuarios: {
    name: string;
    email: string;
  };
}

export default function HomePage() {
  // Usar hooks optimizados con SWR
  const { noticias: mainData, isLoading: mainLoading } = useMainArticle();
  const { breakingNews, isLoading: breakingLoading } = useBreakingNews();
  const { recentNews, isLoading: recentLoading } = useRecentNews(20);

  // Extraer datos
  const mainArticle = mainData && mainData.length > 0 ? mainData[0] as Noticia : null;

  // Loading state combinado
  const loading = mainLoading || breakingLoading || recentLoading;

  if (loading) {
    return <SkeletonPage />;
  }

  return (
    <div className="min-h-screen bg-white">
      <NYTHeader />

      <main className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-10 py-6 lg:py-8">
        {/* Main Content with Sidebar on Desktop */}
        <div className="flex gap-8">
          {/* Main Content */}
          <div className="flex-1 min-w-0">
            {/* Últimas Noticias - INICIO DEL HOME */}
            <div className="mb-6 lg:mb-8">
              <h2 className="text-2xl sm:text-3xl font-bold mb-4 lg:mb-6" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                Últimas Noticias
              </h2>
            </div>

            {/* Main Headline - Primera noticia destacada */}
            {mainArticle && (
              <div className="mb-8 lg:mb-12">
                <MainHeadline article={{
                  id: mainArticle.id,
                  title: mainArticle.title,
                  subtitle: mainArticle.subtitle,
                  excerpt: mainArticle.excerpt,
                  image_url: mainArticle.image_url,
                  slug: mainArticle.slug,
                  category_slug: mainArticle.categorias?.slug || 'politica',
                  published_at: mainArticle.published_at,
                  views: mainArticle.views
                }} />
                      </div>
            )}

            {/* Breaking News / Live Section */}
            {breakingNews.length > 0 && (
              <div className="mb-8 lg:mb-12">
                <LiveSection article={{
                  id: breakingNews[0].id,
                  title: breakingNews[0].title,
                  excerpt: breakingNews[0].excerpt,
                  image_url: breakingNews[0].image_url,
                  slug: breakingNews[0].slug,
                  category_slug: breakingNews[0].categorias?.slug || 'politica',
                  published_at: breakingNews[0].published_at,
                  updateCount: 4
                }} />
                    </div>
            )}

            {/* Secondary Headlines - Mobile-First Responsive */}
            {recentNews.length > 0 ? (
              <div className="space-y-0">
                {recentNews.map((article: any) => (
                  <article key={article.id} className="mb-6 pb-6 lg:mb-8 lg:pb-8 border-b border-gray-300">
                    {/* Mobile-First: Stack vertically */}
                    <div className="flex flex-col gap-4">
                      {/* Image First on Mobile - Better UX */}
                      <div className="w-full relative">
                        <Link href={`/${article.categorias?.slug || 'politica'}/${article.slug}`}>
                          {article.image_url ? (
                            <div className="relative w-full aspect-video overflow-hidden rounded-sm bg-gray-100">
                              <NewsImage
                                src={article.image_url}
                                alt={article.title}
                                fill
                                className="object-contain hover:scale-105 transition-transform duration-300"
                                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 600px"
                                priority={false}
                              />
                            </div>
                          ) : (
                            <div className="relative w-full aspect-video bg-gray-100 flex items-center justify-center rounded-sm">
                              <span className="text-gray-400 text-sm">Sin imagen</span>
                            </div>
                          )}
                        </Link>
                      </div>

                      {/* Text Content - Full Width on Mobile */}
                      <div className="w-full">
                        <Link href={`/${article.categorias?.slug || 'politica'}/${article.slug}`}>
                          <h2 className="text-[18px] sm:text-[20px] lg:text-[22px] font-bold mb-3 hover:opacity-80 transition leading-tight" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                            {article.title}
                          </h2>
                        </Link>
                        {article.excerpt && (
                          <p className="text-[14px] sm:text-[15px] lg:text-[16px] leading-relaxed line-clamp-3 mb-3" style={{ color: 'var(--nyt-text-secondary)', fontFamily: 'var(--font-georgia)' }}>
                            {article.excerpt}
                          </p>
                        )}
                        <p className="text-[10px] sm:text-[11px]" style={{ color: 'var(--nyt-text-gray)' }}>
                          5 MIN READ
                        </p>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="mb-8 pb-8 border-b border-black">
                <p className="text-lg mb-2" style={{ color: 'var(--nyt-text-gray)', fontFamily: 'var(--font-georgia)' }}>
                  Cargando las últimas noticias...
                </p>
                <p className="text-sm" style={{ color: 'var(--nyt-text-gray)' }}>
                  Por favor, espera mientras se cargan las noticias más recientes.
                </p>
              </div>
            )}
          </div>

          {/* Sidebar - Hidden on Mobile */}
          <Sidebar />
        </div>
      </main>

      {/* Footer - NYT Style */}
      <footer className="border-t border-gray-300 mt-16 py-8" style={{ borderTopWidth: '1px', borderTopColor: 'var(--nyt-border)' }}>
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-10">
          {/* Secciones */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-6 mb-8">
            <div>
              <h5 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--nyt-text-primary)', fontFamily: 'var(--font-helvetica)' }}>Política</h5>
              <Link href="/politica" className="block text-sm mb-2 hover:underline" style={{ color: 'var(--nyt-text-gray)' }}>Ver todo</Link>
            </div>
            <div>
              <h5 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--nyt-text-primary)', fontFamily: 'var(--font-helvetica)' }}>Economía</h5>
              <Link href="/economia" className="block text-sm mb-2 hover:underline" style={{ color: 'var(--nyt-text-gray)' }}>Ver todo</Link>
            </div>
            <div>
              <h5 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--nyt-text-primary)', fontFamily: 'var(--font-helvetica)' }}>Judicial</h5>
              <Link href="/judicial" className="block text-sm mb-2 hover:underline" style={{ color: 'var(--nyt-text-gray)' }}>Ver todo</Link>
            </div>
            <div>
              <h5 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--nyt-text-primary)', fontFamily: 'var(--font-helvetica)' }}>Internacional</h5>
              <Link href="/internacional" className="block text-sm mb-2 hover:underline" style={{ color: 'var(--nyt-text-gray)' }}>Ver todo</Link>
            </div>
            <div>
              <h5 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--nyt-text-primary)', fontFamily: 'var(--font-helvetica)' }}>Sociedad</h5>
              <Link href="/sociedad" className="block text-sm mb-2 hover:underline" style={{ color: 'var(--nyt-text-gray)' }}>Ver todo</Link>
            </div>
          </div>

          {/* Legal */}
          <div className="border-t border-gray-200 pt-6 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex gap-4 text-xs" style={{ color: 'var(--nyt-text-gray)' }}>
              <Link href="/terminos" className="hover:underline">Términos de Servicio</Link>
              <span>|</span>
              <Link href="/privacidad" className="hover:underline">Política de Privacidad</Link>
            </div>
            <div className="text-xs" style={{ color: 'var(--nyt-text-gray)' }}>
              © {new Date().getFullYear()} Política Argentina
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
