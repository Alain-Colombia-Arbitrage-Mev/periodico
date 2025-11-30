'use client';

import Image from 'next/image';
import Link from 'next/link';
import NYTHeader from '@/components/nyt/Header';
import { Clock, Eye, Share2, ArrowLeft } from 'lucide-react';
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
  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: article.title,
          text: article.excerpt,
          url: window.location.href,
        });
      } catch (err) {
        console.log('Error sharing:', err);
      }
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* VERSION: mobile-first-v2 - 2024-11-30 */}
      <NYTHeader />

      {/* Mobile-first Article Layout */}
      <main className="w-full">
        {/* Back Button - Mobile Only */}
        <div className="sticky top-[60px] z-40 bg-white border-b border-gray-200 px-4 py-2 md:hidden">
          <div className="flex items-center justify-between">
            <Link
              href={`/${article.categorySlug}`}
              className="flex items-center gap-2 text-sm font-medium text-gray-600"
            >
              <ArrowLeft className="w-4 h-4" />
              {article.category}
            </Link>
            <button
              onClick={handleShare}
              className="p-2 rounded-full hover:bg-gray-100 transition"
              aria-label="Compartir"
            >
              <Share2 className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Featured Image - Full Width on Mobile */}
        <div className="relative w-full aspect-[16/9] md:aspect-[21/9] bg-gray-100">
          <Image
            src={article.imageUrl}
            alt={article.title}
            fill
            className="object-cover"
            priority
            sizes="100vw"
          />
          {/* Gradient Overlay for Mobile */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent md:hidden" />

          {/* Category Badge on Image - Mobile */}
          <div className="absolute bottom-4 left-4 md:hidden">
            <span className="inline-block px-3 py-1 text-xs font-bold uppercase tracking-wide bg-white text-black rounded">
              {article.category}
            </span>
          </div>
        </div>

        {/* Article Content Container - Full width on mobile */}
        <div className="w-full px-4 md:max-w-[720px] md:mx-auto md:px-6 lg:px-8">

          {/* Desktop Breadcrumb */}
          <nav className="hidden md:flex items-center gap-2 text-sm text-gray-500 py-4 border-b border-gray-200">
            <Link href="/" className="hover:text-black transition">
              Inicio
            </Link>
            <span>/</span>
            <Link href={`/${article.categorySlug}`} className="hover:text-black transition">
              {article.category}
            </Link>
          </nav>

          {/* Article Header */}
          <header className="py-6 md:py-8">
            {/* Category - Desktop Only */}
            <div className="hidden md:block mb-4">
              <Link
                href={`/${article.categorySlug}`}
                className="inline-block text-sm font-bold uppercase tracking-wide text-blue-600 hover:text-blue-800 transition"
              >
                {article.category}
              </Link>
            </div>

            {/* Title */}
            <h1
              className="text-[1.75rem] leading-[1.2] md:text-4xl lg:text-5xl font-bold mb-4 md:mb-6"
              style={{ fontFamily: 'var(--font-georgia)', color: '#1a1a1a' }}
            >
              {article.title}
            </h1>

            {/* Subtitle */}
            {article.subtitle && (
              <p
                className="text-lg md:text-xl text-gray-600 leading-relaxed mb-4 md:mb-6"
                style={{ fontFamily: 'var(--font-georgia)' }}
              >
                {article.subtitle}
              </p>
            )}

            {/* Excerpt */}
            <p
              className="text-base md:text-lg text-gray-700 leading-relaxed pb-4 md:pb-6 border-b border-gray-200"
              style={{ fontFamily: 'var(--font-georgia)' }}
            >
              {article.excerpt}
            </p>

            {/* Meta Information */}
            <div className="flex flex-wrap items-center gap-3 md:gap-4 pt-4 text-sm text-gray-500">
              <time className="flex items-center gap-1.5">
                <Clock className="w-4 h-4" />
                <span>
                  {formatDistanceToNow(article.publishedAt, {
                    addSuffix: true,
                    locale: es
                  })}
                </span>
              </time>
              <span className="w-1 h-1 rounded-full bg-gray-400" />
              <span className="flex items-center gap-1.5">
                <Eye className="w-4 h-4" />
                {article.views.toLocaleString()} lecturas
              </span>
              <span className="w-1 h-1 rounded-full bg-gray-400" />
              <span>{article.readingTime} min de lectura</span>

              {/* Share Button - Desktop */}
              <button
                onClick={handleShare}
                className="hidden md:flex items-center gap-1.5 ml-auto text-gray-600 hover:text-black transition"
              >
                <Share2 className="w-4 h-4" />
                Compartir
              </button>
            </div>
          </header>

          {/* Article Body */}
          <article className="pb-8 md:pb-12">
            <div
              className="article-content prose prose-lg max-w-none"
              dangerouslySetInnerHTML={{ __html: article.content }}
            />

            <style jsx global>{`
              .article-content {
                font-family: var(--font-georgia), Georgia, serif;
              }

              .article-content p {
                font-size: 1.0625rem;
                line-height: 1.8;
                color: #1a1a1a;
                margin-bottom: 1.5rem;
              }

              .article-content p:first-of-type {
                font-size: 1.125rem;
              }

              .article-content h2,
              .article-content h3 {
                font-weight: 700;
                color: #1a1a1a;
                margin-top: 2rem;
                margin-bottom: 1rem;
              }

              .article-content h2 {
                font-size: 1.5rem;
              }

              .article-content h3 {
                font-size: 1.25rem;
              }

              .article-content a {
                color: #2563eb;
                text-decoration: underline;
              }

              .article-content blockquote {
                border-left: 4px solid #e5e7eb;
                padding-left: 1rem;
                margin: 1.5rem 0;
                font-style: italic;
                color: #4b5563;
              }

              .article-content ul,
              .article-content ol {
                margin: 1.5rem 0;
                padding-left: 1.5rem;
              }

              .article-content li {
                margin-bottom: 0.5rem;
              }

              .article-content img {
                max-width: 100%;
                height: auto;
                border-radius: 0.5rem;
                margin: 1.5rem 0;
              }

              @media (min-width: 768px) {
                .article-content p {
                  font-size: 1.125rem;
                  text-align: justify;
                }

                .article-content p:first-of-type {
                  font-size: 1.25rem;
                }
              }
            `}</style>
          </article>

          {/* Tags */}
          {article.tags.length > 0 && (
            <div className="py-6 border-t border-gray-200">
              <h3 className="text-sm font-bold uppercase tracking-wide text-gray-500 mb-3">
                Temas relacionados
              </h3>
              <div className="flex flex-wrap gap-2">
                {article.tags.map((tag, index) => (
                  <Link
                    key={index}
                    href={`/tags/${tag.toLowerCase().replace(/\s+/g, '-')}`}
                    className="px-3 py-1.5 text-sm font-medium bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition"
                  >
                    {tag}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Related Articles */}
          {relatedArticles.length > 0 && (
            <section className="py-8 border-t border-gray-200">
              <h2
                className="text-xl md:text-2xl font-bold mb-6"
                style={{ fontFamily: 'var(--font-georgia)' }}
              >
                Seguir leyendo
              </h2>

              <div className="space-y-6 md:space-y-0 md:grid md:grid-cols-2 md:gap-6">
                {relatedArticles.slice(0, 4).map((related) => (
                  <Link
                    key={related.id}
                    href={`/${related.categorySlug}/${related.slug}`}
                    className="group block"
                  >
                    <article className="flex gap-4 md:flex-col">
                      {/* Image */}
                      <div className="relative w-24 h-24 md:w-full md:h-40 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100">
                        <Image
                          src={related.imageUrl}
                          alt={related.title}
                          fill
                          className="object-cover group-hover:scale-105 transition-transform duration-300"
                          sizes="(max-width: 768px) 96px, 50vw"
                        />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <span className="text-xs font-bold uppercase tracking-wide text-blue-600">
                          {related.category}
                        </span>
                        <h3
                          className="mt-1 text-base md:text-lg font-bold line-clamp-3 group-hover:text-blue-600 transition"
                          style={{ fontFamily: 'var(--font-georgia)' }}
                        >
                          {related.title}
                        </h3>
                      </div>
                    </article>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Footer */}
        <footer className="bg-gray-50 border-t border-gray-200 mt-8">
          <div className="w-full px-4 md:max-w-[720px] md:mx-auto md:px-6 lg:px-8 py-8 md:py-12">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
              <div>
                <h4 className="font-bold text-sm uppercase tracking-wide mb-3">Noticias</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li><Link href="/politica" className="hover:text-black transition">Política</Link></li>
                  <li><Link href="/economia" className="hover:text-black transition">Economía</Link></li>
                  <li><Link href="/judicial" className="hover:text-black transition">Judicial</Link></li>
                  <li><Link href="/internacional" className="hover:text-black transition">Internacional</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-bold text-sm uppercase tracking-wide mb-3">Sociedad</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li><Link href="/sociedad" className="hover:text-black transition">Sociedad</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-bold text-sm uppercase tracking-wide mb-3">Legal</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li><Link href="/terminos" className="hover:text-black transition">Términos</Link></li>
                  <li><Link href="/privacidad" className="hover:text-black transition">Privacidad</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-bold text-sm uppercase tracking-wide mb-3">Contacto</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li><Link href="/contacto" className="hover:text-black transition">Contacto</Link></li>
                </ul>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-200 text-center text-sm text-gray-500">
              <p>&copy; {new Date().getFullYear()} Política Argentina. Todos los derechos reservados.</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
