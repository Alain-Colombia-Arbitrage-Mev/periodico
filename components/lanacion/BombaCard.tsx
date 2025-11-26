/**
 * BOMBA CARD - La Nación Style
 * Featured news with dark background and premium styling
 */

'use client';

import Image from 'next/image';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';
import { Eye, Clock } from 'lucide-react';

export interface BombaCardProps {
  id: number;
  title: string;
  subtitle?: string;
  excerpt: string;
  imageUrl: string;
  category: string;
  categorySlug: string;
  author: string;
  publishedAt: Date;
  views: number;
  readingTime?: number;
  slug?: string;
}

export default function BombaCard({
  id,
  title,
  subtitle,
  excerpt,
  imageUrl,
  category,
  categorySlug,
  author,
  publishedAt,
  views,
  readingTime = 5,
  slug = `#${id}`,
}: BombaCardProps) {
  return (
    <Link href={slug} className="ln-bomba block cursor-pointer group">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          {/* Content */}
          <div className="order-2 lg:order-1">
            <span className="ln-bomba-badge">{category}</span>

            <h2 className="ln-bomba-title group-hover:text-blue-300 transition-colors">
              {title}
            </h2>

            {subtitle && (
              <p className="text-xl md:text-2xl font-semibold mb-4" style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                {subtitle}
              </p>
            )}

            <p className="ln-bomba-excerpt">
              {excerpt}
            </p>

            <div className="ln-bomba-meta">
              <span>{author}</span>
              <span>•</span>
              <time>
                {formatDistanceToNow(publishedAt, {
                  addSuffix: true,
                  locale: es,
                })}
              </time>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Eye className="w-4 h-4" />
                {views.toLocaleString()}
              </span>
              {readingTime && (
                <>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {readingTime} min
                  </span>
                </>
              )}
            </div>
          </div>

          {/* Image */}
          <div className="order-1 lg:order-2 relative h-[300px] md:h-[400px] lg:h-[450px] overflow-hidden">
            <Image
              src={imageUrl}
              alt={title}
              fill
              className="object-cover transition-transform duration-500 group-hover:scale-105"
              priority
              sizes="(max-width: 768px) 100vw, 50vw"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
          </div>
        </div>
      </div>
    </Link>
  );
}
