'use client';

import { useEffect, useState } from 'react';
import { supabaseHelpers } from '@/lib/supabase';
import NYTHeader from '@/components/nyt/Header';
import MainHeadline from '@/components/nyt/MainHeadline';
import LiveSection from '@/components/nyt/LiveSection';
import Sidebar from '@/components/nyt/Sidebar';
import Image from 'next/image';
import Link from 'next/link';

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

export default function NYTHomePage() {
  const [mainArticle, setMainArticle] = useState<Noticia | null>(null);
  const [breakingNews, setBreakingNews] = useState<Noticia[]>([]);
  const [recentNews, setRecentNews] = useState<Noticia[]>([]);
  const [featuredArticle, setFeaturedArticle] = useState<Noticia | null>(null);
  const [sideArticles, setSideArticles] = useState<Noticia[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        // Obtener noticia principal (más reciente)
        const { data: mainData, error: mainError } = await supabaseHelpers.getNoticias({
          status: 'published',
          limit: 1
        });

        if (!mainError && mainData && mainData.length > 0) {
          setMainArticle(mainData[0] as Noticia);
        }

        // Obtener noticias de última hora
        const { data: breakingData } = await supabaseHelpers.getNoticias({
          status: 'published',
          limit: 3
        });
        
        if (breakingData) {
          const breaking = breakingData.filter((n: any) => n.is_breaking);
          setBreakingNews(breaking as Noticia[]);
        }

        // Obtener noticias recientes
        const { data: recentData } = await supabaseHelpers.getNoticias({
          status: 'published',
          limit: 10
        });
        
        if (recentData) {
          setRecentNews(recentData.slice(1, 6) as Noticia[]);
        }

        // Obtener artículo destacado para sidebar
        const { data: featuredData } = await supabaseHelpers.getNoticias({
          status: 'published',
          limit: 1,
          offset: 1
        });
        
        if (featuredData && featuredData.length > 0) {
          setFeaturedArticle(featuredData[0] as Noticia);
        }

        // Obtener artículos laterales
        const { data: sideData } = await supabaseHelpers.getNoticias({
          status: 'published',
          limit: 4,
          offset: 2
        });
        
        if (sideData) {
          setSideArticles(sideData as Noticia[]);
        }

      } catch (error) {
        console.error('Error fetching news:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg">Cargando...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <NYTHeader />

      <main className="max-w-[1440px] mx-auto px-10 py-8">
        <div className="flex gap-8">
          {/* Main Content */}
          <div className="flex-1 max-w-[976px]">
            {/* Main Headline */}
            {mainArticle && (
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
            )}

            {/* Breaking News / Live Section */}
            {breakingNews.length > 0 && (
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
            )}

            {/* Secondary Headlines */}
            {recentNews.map((article) => (
              <article key={article.id} className="mb-8 pb-8 border-b border-black">
                <div className="flex gap-6">
                  <div className="flex-1 max-w-[348px]">
                    <Link href={`/${article.categorias?.slug || 'politica'}/${article.slug}`}>
                      <h2 className="font-serif text-[20px] font-bold mb-4 hover:opacity-80 transition">
                        {article.title}
                      </h2>
                    </Link>
                    <p className="text-[16px] text-[#5a5a5a] mb-4 leading-relaxed">
                      {article.excerpt}
                    </p>
                    <p className="text-[10px] text-[#5a5a5a]">
                      5 MIN READ
                    </p>
                  </div>
                  <div className="flex-1 max-w-[592px]">
                    <Link href={`/${article.categorias?.slug || 'politica'}/${article.slug}`}>
                      <div className="relative w-full h-[356px]">
                        <Image
                          src={article.image_url}
                          alt={article.title}
                          fill
                          className="object-cover"
                          sizes="592px"
                        />
                      </div>
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>

          {/* Sidebar */}
          <div className="w-[335px]">
            <Sidebar
              featuredArticle={featuredArticle ? {
                id: featuredArticle.id,
                title: featuredArticle.title,
                excerpt: featuredArticle.excerpt,
                image_url: featuredArticle.image_url,
                slug: featuredArticle.slug,
                category_slug: featuredArticle.categorias?.slug || 'politica',
                published_at: featuredArticle.published_at
              } : undefined}
              sideArticles={sideArticles.map(a => ({
                id: a.id,
                title: a.title,
                image_url: a.image_url,
                slug: a.slug,
                category_slug: a.categorias?.slug || 'politica',
                published_at: a.published_at
              }))}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t-2 border-black mt-16 py-12">
        <div className="max-w-[1440px] mx-auto px-10">
          <div className="grid grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="font-bold text-sm uppercase mb-4">Noticias</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/politica" className="hover:underline">Política</Link></li>
                <li><Link href="/economia" className="hover:underline">Economía</Link></li>
                <li><Link href="/judicial" className="hover:underline">Judicial</Link></li>
                <li><Link href="/internacional" className="hover:underline">Internacional</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-sm uppercase mb-4">Opinión</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/opinion" className="hover:underline">Editoriales</Link></li>
                <li><Link href="/opinion" className="hover:underline">Columnistas</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-sm uppercase mb-4">Más</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/sobre-nosotros" className="hover:underline">Sobre Nosotros</Link></li>
                <li><Link href="/contacto" className="hover:underline">Contacto</Link></li>
                <li><Link href="/terminos" className="hover:underline">Términos</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-sm uppercase mb-4">Suscribirse</h4>
              <p className="text-sm text-gray-600 mb-4">
                Accede a todas las noticias
              </p>
              <button className="bg-[#587c94] text-white text-sm px-4 py-2 rounded hover:bg-[#4a6a7f] transition">
                Suscribirse
              </button>
            </div>
          </div>
          <div className="border-t border-gray-300 pt-8 text-center text-sm text-gray-600">
            <p>&copy; 2025 Política Argentina. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

