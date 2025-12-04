'use client';

import Image from 'next/image';
import Link from 'next/link';
import NYTHeader from '@/components/nyt/Header';
import Sidebar from '@/components/nyt/Sidebar';
import { Clock, Eye, ChevronRight } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface Article {
  id: string;
  title: string;
  subtitle?: string;
  excerpt: string;
  content: string;
  imageUrl: string;
  publishedAt: Date;
  updatedAt?: Date;
  category: string;
  categorySlug: string;
  tags: string[];
  views: number;
  readingTime: number;
}

interface RelatedArticle {
  id: string;
  title: string;
  imageUrl: string;
  category: string;
  categorySlug: string;
  slug: string;
}

interface ArticlePageProps {
  article: Article;
  relatedArticles?: RelatedArticle[];
}

export default function ArticlePage({ article, relatedArticles = [] }: ArticlePageProps) {
  return (
    <div className="min-h-screen bg-white">
      <NYTHeader />

      {/* Breadcrumb */}
      <div className="max-w-[1440px] mx-auto px-10 py-4">
        <nav className="flex items-center gap-2 text-sm" style={{ color: 'var(--nyt-text-gray)' }}>
          <Link href="/" className="hover:underline">
            Inicio
          </Link>
          <ChevronRight className="w-4 h-4" />
          <Link href={`/${article.categorySlug}`} className="hover:underline">
            {article.category}
          </Link>
          <ChevronRight className="w-4 h-4" />
          <span className="truncate max-w-md">{article.title}</span>
        </nav>
      </div>

      {/* Main Content */}
      <main className="max-w-[1440px] mx-auto px-10 pb-12">
        <div className="flex gap-8">
          {/* Article Content */}
          <article className="flex-1 max-w-[976px]">
            {/* Header */}
            <header className="mb-8 pb-8 border-b border-black">
              {/* Title */}
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                {article.title}
              </h1>

              {/* Subtitle */}
              {article.subtitle && (
                <p className="text-xl md:text-2xl font-medium leading-relaxed mb-6" style={{ color: 'var(--nyt-text-secondary)', fontFamily: 'var(--font-georgia)' }}>
                  {article.subtitle}
                </p>
              )}

              {/* Excerpt */}
              <p className="text-lg leading-relaxed mb-6 pb-6 border-b" style={{ color: 'var(--nyt-text-secondary)', fontFamily: 'var(--font-georgia)', borderColor: 'var(--nyt-divider)' }}>
                {article.excerpt}
              </p>

              {/* Meta Information */}
              <div className="flex flex-wrap items-center gap-4 text-sm" style={{ color: 'var(--nyt-text-gray)' }}>
                <time className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {formatDistanceToNow(article.publishedAt, {
                    addSuffix: true,
                    locale: es
                  })}
                </time>
                <span>•</span>
                <span className="flex items-center gap-1">
                  <Eye className="w-4 h-4" />
                  {article.views.toLocaleString()} lecturas
                </span>
                <span>•</span>
                <span>{article.readingTime} min de lectura</span>
              </div>
            </header>

            {/* Featured Image */}
            <div className="relative w-full h-[500px] md:h-[600px] mb-8">
              <Image
                src={article.imageUrl}
                alt={article.title}
                fill
                className="object-cover"
                priority
                sizes="976px"
              />
            </div>

            {/* Content */}
            <div className="prose prose-lg max-w-none mb-12">
              <style jsx>{`
                .article-content :global(p) {
                  margin-bottom: 1.5rem;
                  text-align: justify;
                  font-family: var(--font-georgia);
                  color: var(--nyt-text-primary);
                  font-size: 1.125rem;
                  line-height: 1.8;
                }
                .article-content :global(p:first-of-type) {
                  font-size: 1.25rem;
                  line-height: 1.75;
                }
                .article-content :global(p:last-of-type) {
                  margin-bottom: 0;
                }
              `}</style>
              <div
                className="article-content"
                dangerouslySetInnerHTML={{ __html: article.content }}
              />
            </div>

            {/* Tags */}
            {article.tags.filter(tag => tag.toLowerCase() !== 'auto').length > 0 && (
              <div className="mt-12 pt-8 border-t" style={{ borderColor: 'var(--nyt-divider)' }}>
                <h3 className="text-lg font-semibold mb-4" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                  Etiquetas:
                </h3>
                <div className="flex flex-wrap gap-2">
                  {article.tags.filter(tag => tag.toLowerCase() !== 'auto').map((tag, index) => (
                    <Link
                      key={index}
                      href={`/tags/${tag.toLowerCase().replace(/\s+/g, '-')}`}
                      className="px-4 py-2 rounded-full text-sm font-medium transition-colors"
                      style={{ 
                        backgroundColor: 'var(--nyt-bg-gray)',
                        color: 'var(--nyt-text-dark-gray)'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--nyt-button-bg)';
                        e.currentTarget.style.color = 'white';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--nyt-bg-gray)';
                        e.currentTarget.style.color = 'var(--nyt-text-dark-gray)';
                      }}
                    >
                      #{tag}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Related Articles */}
            {relatedArticles.length > 0 && (
              <div className="mt-12 pt-8 border-t-2 border-black">
                <h3 className="text-2xl font-bold mb-6" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                  Artículos Relacionados
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {relatedArticles.map((related) => (
                    <Link
                      key={related.id}
                      href={`/${related.categorySlug}/${related.slug}`}
                      className="group"
                    >
                      <article className="border border-black overflow-hidden hover:opacity-80 transition">
                        <div className="relative h-48">
                          <Image
                            src={related.imageUrl}
                            alt={related.title}
                            fill
                            className="object-cover"
                            sizes="(max-width: 768px) 100vw, 33vw"
                          />
                        </div>
                        <div className="p-4">
                          <h4 className="text-lg font-bold line-clamp-3 group-hover:opacity-80 transition" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                            {related.title}
                          </h4>
                        </div>
                      </article>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </article>

          {/* Sidebar */}
          <div className="w-[335px]">
            <Sidebar />
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
              <p className="text-sm mb-4" style={{ color: 'var(--nyt-text-gray)' }}>
                Accede a todas las noticias
              </p>
              <button className="text-white text-sm px-4 py-2 rounded transition" style={{ backgroundColor: 'var(--nyt-button-bg)' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--nyt-button-hover)'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--nyt-button-bg)'}>
                Suscribirse
              </button>
            </div>
          </div>
          <div className="border-t pt-8 text-center text-sm" style={{ borderColor: 'var(--nyt-divider)', color: 'var(--nyt-text-gray)' }}>
            <p>&copy; 2025 Política Argentina. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
