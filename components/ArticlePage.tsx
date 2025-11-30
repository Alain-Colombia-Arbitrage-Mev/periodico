'use client';

import Image from 'next/image';
import Link from 'next/link';
import NYTHeader from '@/components/nyt/Header';
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
      <div className="max-w-[1440px] mx-auto px-3 sm:px-4 md:px-10 py-3 md:py-4">
        <nav className="flex items-center gap-1 sm:gap-2 text-[10px] sm:text-xs md:text-sm overflow-x-auto whitespace-nowrap" style={{ color: 'var(--nyt-text-gray)' }}>
          <Link href="/" className="hover:underline flex-shrink-0">
            Inicio
          </Link>
          <ChevronRight className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
          <Link href={`/${article.categorySlug}`} className="hover:underline flex-shrink-0">
            {article.category}
          </Link>
          <ChevronRight className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
          <span className="truncate max-w-[120px] sm:max-w-[200px] md:max-w-md">{article.title}</span>
        </nav>
      </div>

      {/* Main Content - Full width, no sidebar on article pages */}
      <main className="max-w-[900px] mx-auto px-3 sm:px-4 md:px-10 pb-8 md:pb-12 overflow-x-hidden">
        {/* Article Content */}
        <article className="w-full">
            {/* Header */}
            <header className="mb-6 md:mb-8 pb-6 md:pb-8 border-b border-black">
              {/* Title */}
              <h1 className="text-2xl sm:text-3xl md:text-5xl lg:text-6xl font-bold leading-tight mb-4 md:mb-6" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                {article.title}
              </h1>

              {/* Subtitle */}
              {article.subtitle && (
                <p className="text-base sm:text-lg md:text-2xl font-medium leading-relaxed mb-4 md:mb-6" style={{ color: 'var(--nyt-text-secondary)', fontFamily: 'var(--font-georgia)' }}>
                  {article.subtitle}
                </p>
              )}

              {/* Excerpt */}
              <p className="text-sm sm:text-base md:text-lg leading-relaxed mb-4 md:mb-6 pb-4 md:pb-6 border-b" style={{ color: 'var(--nyt-text-secondary)', fontFamily: 'var(--font-georgia)', borderColor: 'var(--nyt-divider)' }}>
                {article.excerpt}
              </p>

              {/* Meta Information */}
              <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm" style={{ color: 'var(--nyt-text-gray)' }}>
                <time className="flex items-center gap-1">
                  <Clock className="w-3 h-3 sm:w-4 sm:h-4" />
                  {formatDistanceToNow(article.publishedAt, {
                    addSuffix: true,
                    locale: es
                  })}
                </time>
                <span className="hidden sm:inline">•</span>
                <span className="flex items-center gap-1">
                  <Eye className="w-3 h-3 sm:w-4 sm:h-4" />
                  {article.views.toLocaleString()} lecturas
                </span>
                <span className="hidden sm:inline">•</span>
                <span>{article.readingTime} min</span>
              </div>
            </header>

            {/* Featured Image */}
            <div className="relative w-full h-[200px] sm:h-[300px] md:h-[500px] lg:h-[600px] mb-6 md:mb-8">
              <Image
                src={article.imageUrl}
                alt={article.title}
                fill
                className="object-cover"
                priority
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 100vw, 976px"
              />
            </div>

            {/* Content */}
            <div className="prose prose-sm sm:prose-base md:prose-lg max-w-none mb-8 md:mb-12">
              <style jsx>{`
                .article-content :global(p) {
                  margin-bottom: 1rem;
                  text-align: left;
                  font-family: var(--font-georgia);
                  color: var(--nyt-text-primary);
                  font-size: 0.875rem;
                  line-height: 1.7;
                  word-wrap: break-word;
                  overflow-wrap: break-word;
                }
                @media (min-width: 640px) {
                  .article-content :global(p) {
                    margin-bottom: 1.25rem;
                    font-size: 1rem;
                    line-height: 1.75;
                    text-align: justify;
                  }
                }
                @media (min-width: 768px) {
                  .article-content :global(p) {
                    margin-bottom: 1.5rem;
                    font-size: 1.125rem;
                    line-height: 1.8;
                  }
                }
                .article-content :global(p:first-of-type) {
                  font-size: 1rem;
                  line-height: 1.7;
                }
                @media (min-width: 768px) {
                  .article-content :global(p:first-of-type) {
                    font-size: 1.25rem;
                    line-height: 1.75;
                  }
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
            {article.tags.length > 0 && (
              <div className="mt-8 md:mt-12 pt-6 md:pt-8 border-t" style={{ borderColor: 'var(--nyt-divider)' }}>
                <h3 className="text-base md:text-lg font-semibold mb-3 md:mb-4" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                  Etiquetas:
                </h3>
                <div className="flex flex-wrap gap-1.5 sm:gap-2">
                  {article.tags.map((tag, index) => (
                    <Link
                      key={index}
                      href={`/tags/${tag.toLowerCase().replace(/\s+/g, '-')}`}
                      className="px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-full text-xs sm:text-sm font-medium transition-colors"
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
              <div className="mt-8 md:mt-12 pt-6 md:pt-8 border-t-2 border-black">
                <h3 className="text-lg sm:text-xl md:text-2xl font-bold mb-4 md:mb-6" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                  Artículos Relacionados
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
                  {relatedArticles.map((related) => (
                    <Link
                      key={related.id}
                      href={`/${related.categorySlug}/${related.slug}`}
                      className="group"
                    >
                      <article className="border border-black overflow-hidden hover:opacity-80 transition">
                        <div className="relative h-32 sm:h-40 md:h-48">
                          <Image
                            src={related.imageUrl}
                            alt={related.title}
                            fill
                            className="object-cover"
                            sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, 33vw"
                          />
                        </div>
                        <div className="p-3 sm:p-4">
                          <h4 className="text-sm sm:text-base md:text-lg font-bold line-clamp-3 group-hover:opacity-80 transition" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
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
      </main>

      {/* Footer */}
      <footer className="border-t-2 border-black mt-8 md:mt-16 py-8 md:py-12">
        <div className="max-w-[1440px] mx-auto px-3 sm:px-4 md:px-10">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 md:gap-8 mb-6 md:mb-8">
            <div>
              <h4 className="font-bold text-xs sm:text-sm uppercase mb-2 sm:mb-4">Noticias</h4>
              <ul className="space-y-1 sm:space-y-2 text-xs sm:text-sm">
                <li><Link href="/politica" className="hover:underline">Política</Link></li>
                <li><Link href="/economia" className="hover:underline">Economía</Link></li>
                <li><Link href="/judicial" className="hover:underline">Judicial</Link></li>
                <li><Link href="/internacional" className="hover:underline">Internacional</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-xs sm:text-sm uppercase mb-2 sm:mb-4">Opinión</h4>
              <ul className="space-y-1 sm:space-y-2 text-xs sm:text-sm">
                <li><Link href="/opinion" className="hover:underline">Editoriales</Link></li>
                <li><Link href="/opinion" className="hover:underline">Columnistas</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-xs sm:text-sm uppercase mb-2 sm:mb-4">Más</h4>
              <ul className="space-y-1 sm:space-y-2 text-xs sm:text-sm">
                <li><Link href="/sobre-nosotros" className="hover:underline">Sobre Nosotros</Link></li>
                <li><Link href="/contacto" className="hover:underline">Contacto</Link></li>
                <li><Link href="/terminos" className="hover:underline">Términos</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-xs sm:text-sm uppercase mb-2 sm:mb-4">Suscribirse</h4>
              <p className="text-xs sm:text-sm mb-2 sm:mb-4" style={{ color: 'var(--nyt-text-gray)' }}>
                Accede a todas las noticias
              </p>
              <button className="text-white text-xs sm:text-sm px-3 sm:px-4 py-1.5 sm:py-2 rounded transition" style={{ backgroundColor: 'var(--nyt-button-bg)' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--nyt-button-hover)'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'var(--nyt-button-bg)'}>
                Suscribirse
              </button>
            </div>
          </div>
          <div className="border-t pt-6 md:pt-8 text-center text-xs sm:text-sm" style={{ borderColor: 'var(--nyt-divider)', color: 'var(--nyt-text-gray)' }}>
            <p>&copy; 2025 Política Argentina. Todos los derechos reservados.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
