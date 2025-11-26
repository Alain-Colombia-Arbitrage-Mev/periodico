'use client';

import { LucideIcon } from 'lucide-react';

interface CategoryHeroProps {
  title: string;
  description: string;
  icon: LucideIcon;
  color: string;
  gradient: string;
  count?: number;
}

export default function CategoryHero({
  title,
  description,
  icon: Icon,
  color,
  gradient,
  count
}: CategoryHeroProps) {
  return (
    <section className="relative overflow-hidden mb-8">
      {/* Background with gradient */}
      <div
        className="absolute inset-0 opacity-5"
        style={{
          background: gradient
        }}
      />

      {/* Pattern overlay */}
      <div className="absolute inset-0 opacity-[0.03]">
        <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      <div className="container mx-auto px-4 py-12 md:py-16 relative z-10">
        <div className="max-w-4xl">
          {/* Icon */}
          <div
            className="inline-flex items-center justify-center w-16 h-16 md:w-20 md:h-20 rounded-2xl mb-6 shadow-lg"
            style={{
              background: gradient
            }}
          >
            <Icon className="w-8 h-8 md:w-10 md:h-10 text-white" />
          </div>

          {/* Title */}
          <h1
            className="text-4xl md:text-5xl lg:text-6xl font-serif font-bold mb-4 tracking-tight"
            style={{ color: 'var(--ln-neutral-900)' }}
          >
            {title}
          </h1>

          {/* Description */}
          <p
            className="text-lg md:text-xl mb-6 leading-relaxed max-w-2xl"
            style={{ color: 'var(--ln-neutral-600)' }}
          >
            {description}
          </p>

          {/* Stats */}
          {count !== undefined && (
            <div className="flex items-center gap-6 flex-wrap">
              <div
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg backdrop-blur-sm"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  border: '1px solid var(--ln-neutral-200)'
                }}
              >
                <span className="text-2xl font-bold" style={{ color }}>
                  {count}
                </span>
                <span className="text-sm font-medium" style={{ color: 'var(--ln-neutral-600)' }}>
                  noticias publicadas
                </span>
              </div>

              <div className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: color }} />
                <span className="text-sm font-medium" style={{ color: 'var(--ln-neutral-500)' }}>
                  Actualizado continuamente
                </span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-white to-transparent" />
    </section>
  );
}
