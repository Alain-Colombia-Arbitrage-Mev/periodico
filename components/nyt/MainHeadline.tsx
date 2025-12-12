'use client';

import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import NewsImage from '@/components/NewsImage';

interface MainHeadlineProps {
  article: {
    id: string;
    title: string;
    subtitle?: string;
    excerpt: string;
    image_url: string;
    slug: string;
    category_slug: string;
    published_at: string;
    views?: number;
  };
}

export default function MainHeadline({ article }: MainHeadlineProps) {
  return (
    <article className="mb-6 md:mb-8 pb-6 md:pb-8 border-b border-[var(--border-soft)]">
      {/* Mobile-First Layout: Stack Vertically */}
      <div className="flex flex-col gap-4 md:gap-6">
        {/* Image First - Better Mobile UX */}
        <div className="w-full">
          <Link href={`/${article.category_slug}/${article.slug}`} className="block">
            {article.image_url ? (
              <div className="relative w-full aspect-video md:aspect-[16/10] overflow-hidden rounded-sm bg-gray-100">
                <NewsImage
                  src={article.image_url}
                  alt={article.title}
                  fill
                  className="object-cover hover:scale-105 transition-transform duration-300"
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 100vw, 800px"
                  priority={true}
                />
              </div>
            ) : (
              <div className="relative w-full aspect-video md:aspect-[16/10] bg-gray-100 flex items-center justify-center rounded-sm">
                <span className="text-gray-400 text-sm">Sin imagen</span>
              </div>
            )}
          </Link>
        </div>

        {/* Text Content - Full Width on All Devices */}
        <div className="w-full">
          <div className="space-y-3 md:space-y-4">
            <Link href={`/${article.category_slug}/${article.slug}`} className="block">
              <h1 className="text-[26px] sm:text-[32px] md:text-[40px] lg:text-[44px] font-bold leading-tight hover:opacity-80 transition-opacity duration-200" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                {article.title}
              </h1>
            </Link>

            {article.subtitle && (
              <p className="text-[15px] sm:text-[16px] md:text-[18px] leading-relaxed line-clamp-3 md:line-clamp-none" style={{ color: 'var(--nyt-text-secondary)', fontFamily: 'var(--font-georgia)' }}>
                {article.subtitle}
              </p>
            )}

            {article.excerpt && (
              <p className="text-[14px] sm:text-[15px] md:text-[16px] leading-relaxed line-clamp-3 md:line-clamp-4" style={{ color: 'var(--nyt-text-secondary)', fontFamily: 'var(--font-georgia)' }}>
                {article.excerpt}
              </p>
            )}

            <div className="text-[11px] md:text-[12px] pt-2" style={{ color: 'var(--nyt-text-gray)', fontFamily: 'var(--font-ui)' }}>
              {formatDistanceToNow(new Date(article.published_at), {
                addSuffix: true,
                locale: es
              })}
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}

