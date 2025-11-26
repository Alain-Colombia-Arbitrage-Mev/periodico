'use client';

import Image from 'next/image';
import { Quote } from 'lucide-react';

interface FeaturedOpinionProps {
  title: string;
  excerpt: string;
  author: string;
  authorRole: string;
  authorImage: string;
  category?: string;
}

export default function FeaturedOpinion({
  title = "La Argentina necesita un cambio de rumbo urgente",
  excerpt = "El país se encuentra en una encrucijada histórica. Las decisiones que se tomen en los próximos meses determinarán el futuro de millones de argentinos. Es momento de pensar con responsabilidad y visión de largo plazo.",
  author = "Dr. Juan Pérez",
  authorRole = "Analista Político",
  authorImage = "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop",
  category = "Opinión"
}: FeaturedOpinionProps) {
  return (
    <section className="my-8">
      <div className="container mx-auto px-4">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-l-4 border-blue-600 p-6 md:p-8 relative overflow-hidden">
          {/* Decorative Quote Icon */}
          <div className="absolute top-4 right-4 opacity-10">
            <Quote className="w-24 h-24 text-blue-600" />
          </div>

          {/* Category Badge */}
          <div className="mb-4">
            <span className="inline-block px-3 py-1 bg-blue-600 text-white text-xs font-bold uppercase tracking-wider">
              {category}
            </span>
          </div>

          {/* Title */}
          <h2 className="font-serif text-2xl md:text-3xl lg:text-4xl font-bold text-gray-900 mb-4 relative z-10">
            {title}
          </h2>

          {/* Excerpt */}
          <p className="text-base md:text-lg text-gray-700 leading-relaxed mb-6 relative z-10 max-w-4xl">
            {excerpt}
          </p>

          {/* Author Info */}
          <div className="flex items-center gap-4 relative z-10">
            <div className="relative">
              <div className="w-16 h-16 rounded-full overflow-hidden border-4 border-white shadow-lg">
                <Image
                  src={authorImage}
                  alt={author}
                  width={64}
                  height={64}
                  className="object-cover"
                />
              </div>
              <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-blue-600 rounded-full border-2 border-white flex items-center justify-center">
                <Quote className="w-3 h-3 text-white" />
              </div>
            </div>
            <div>
              <div className="font-bold text-gray-900">{author}</div>
              <div className="text-sm text-gray-600">{authorRole}</div>
            </div>
          </div>

          {/* Read More Link */}
          <div className="mt-6 relative z-10">
            <button className="text-blue-600 hover:text-blue-800 font-semibold text-sm uppercase tracking-wide transition-colors inline-flex items-center gap-2 group">
              Leer artículo completo
              <span className="transform group-hover:translate-x-1 transition-transform">→</span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
