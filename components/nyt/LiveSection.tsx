'use client';

import Image from 'next/image';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

interface LiveSectionProps {
  article: {
    id: string;
    title: string;
    excerpt: string;
    image_url: string;
    slug: string;
    category_slug: string;
    published_at: string;
    updateCount?: number;
  };
}

export default function LiveSection({ article }: LiveSectionProps) {
  const timeAgo = formatDistanceToNow(new Date(article.published_at), {
    addSuffix: false,
    locale: es
  });

  return (
    <section className="mb-8 pb-8 border-b border-black">
      {/* Live Tag and Navigation */}
      <div className="mb-4">
        <div className="flex items-end gap-4 mb-4">
          <span className="text-[16px] font-bold" style={{ color: 'var(--nyt-red-live)' }}>EN VIVO</span>
          <span className="text-[14px]" style={{ color: 'var(--nyt-red-live)' }}>{timeAgo}</span>
        </div>
        
        <div className="flex items-center gap-6 text-[14px]">
          <span className="font-bold">Guerra Israel-Hamas</span>
          <Link href="#" className="hover:underline">Actualizaciones</Link>
          <Link href="#" className="hover:underline">Lo que Sabemos</Link>
          <Link href="#" className="hover:underline">Mapas</Link>
          <Link href="#" className="hover:underline">Fotos</Link>
        </div>
      </div>

      {/* Content */}
      <div className="flex flex-col md:flex-row gap-6">
        {/* Text */}
        <div className="flex-1 md:max-w-[348px] order-2 md:order-1 w-full">
          <div className="space-y-4">
            <Link href={`/${article.category_slug}/${article.slug}`}>
              <h2 className="text-[18px] md:text-[20px] font-bold leading-tight mb-4 hover:opacity-80 transition" style={{ fontFamily: 'var(--font-georgia)', color: 'var(--nyt-text-primary)' }}>
                {article.title}
              </h2>
            </Link>
            
            {article.excerpt && (
              <p className="text-[14px] md:text-[16px] leading-relaxed line-clamp-4 break-words" style={{ color: 'var(--nyt-text-secondary)', fontFamily: 'var(--font-georgia)' }}>
                {article.excerpt}
              </p>
            )}
            
            <div className="flex items-center gap-2">
              <Link 
                href={`/${article.category_slug}/${article.slug}`}
                className="text-[16px] font-medium hover:underline"
                style={{ color: 'var(--nyt-text-dark-gray)' }}
              >
                Ver más actualizaciones
              </Link>
              {article.updateCount && article.updateCount > 0 && (
                <span className="text-white text-[12px] px-2 py-1 rounded" style={{ backgroundColor: 'var(--nyt-text-dark-gray)' }}>
                  {article.updateCount}+
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Image */}
        <div className="flex-1 md:max-w-[592px] order-1 md:order-2 w-full">
          <Link href={`/${article.category_slug}/${article.slug}`}>
            {article.image_url ? (
              <div className="relative w-full h-[250px] md:h-[356px] overflow-hidden">
                <Image
                  src={article.image_url}
                  alt={article.title}
                  fill
                  className="object-cover"
                  sizes="(max-width: 768px) 100vw, 592px"
                  priority={false}
                />
              </div>
            ) : (
              <div className="relative w-full h-[250px] md:h-[356px] bg-gray-200 flex items-center justify-center">
                <span className="text-gray-400 text-sm">Sin imagen</span>
              </div>
            )}
          </Link>
        </div>
      </div>
    </section>
  );
}

