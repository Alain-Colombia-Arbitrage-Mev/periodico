'use client';

/**
 * Skeleton Loaders - Responsive Loading States
 * Mobile-first design with proper touch targets
 */

export function SkeletonMainHeadline() {
  return (
    <article className="mb-6 md:mb-8 pb-6 md:pb-8 border-b border-black animate-pulse">
      <div className="flex flex-col gap-4 md:gap-6">
        {/* Image Skeleton - Shows first on mobile */}
        <div className="w-full aspect-video md:aspect-[16/10] bg-gray-200 rounded-sm"></div>

        {/* Text Content Skeleton */}
        <div className="space-y-3 md:space-y-4">
          {/* Title */}
          <div className="space-y-2">
            <div className="h-6 md:h-8 bg-gray-200 rounded w-full"></div>
            <div className="h-6 md:h-8 bg-gray-200 rounded w-4/5"></div>
          </div>

          {/* Excerpt */}
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-11/12"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>

          {/* Timestamp */}
          <div className="h-3 bg-gray-200 rounded w-24"></div>
        </div>
      </div>
    </article>
  );
}

export function SkeletonArticleCard() {
  return (
    <article className="mb-6 pb-6 border-b border-gray-200 animate-pulse">
      <div className="flex flex-col gap-4">
        {/* Image Skeleton - Mobile First */}
        <div className="w-full aspect-video bg-gray-200 rounded-sm"></div>

        {/* Text Content */}
        <div className="space-y-3">
          {/* Title */}
          <div className="space-y-2">
            <div className="h-5 bg-gray-200 rounded w-full"></div>
            <div className="h-5 bg-gray-200 rounded w-3/4"></div>
          </div>

          {/* Excerpt - Hidden on small mobile */}
          <div className="hidden sm:flex flex-col gap-2">
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>

          {/* Metadata */}
          <div className="h-3 bg-gray-200 rounded w-20"></div>
        </div>
      </div>
    </article>
  );
}

export function SkeletonGrid() {
  return (
    <div className="space-y-0">
      {[1, 2, 3, 4, 5].map((i) => (
        <SkeletonArticleCard key={i} />
      ))}
    </div>
  );
}

export function SkeletonSidebar() {
  return (
    <aside className="space-y-6 animate-pulse">
      {/* Featured Article */}
      <div className="space-y-3 pb-6 border-b border-gray-200">
        <div className="w-full aspect-video bg-gray-200 rounded-sm"></div>
        <div className="space-y-2">
          <div className="h-5 bg-gray-200 rounded w-full"></div>
          <div className="h-5 bg-gray-200 rounded w-4/5"></div>
        </div>
      </div>

      {/* Side Articles */}
      {[1, 2, 3].map((i) => (
        <div key={i} className="space-y-2 pb-4 border-b border-gray-200">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-3 bg-gray-200 rounded w-16"></div>
        </div>
      ))}
    </aside>
  );
}

export function SkeletonPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Main Content Area - No sidebar */}
      <main className="max-w-[900px] mx-auto px-4 sm:px-6 lg:px-10 py-6 lg:py-8">
        <div className="w-full">
          {/* Section Title */}
          <div className="mb-6 lg:mb-8">
            <div className="h-8 bg-gray-200 rounded w-48 animate-pulse"></div>
          </div>

          {/* Main Headline */}
          <SkeletonMainHeadline />

          {/* Articles Grid */}
          <SkeletonGrid />
        </div>
      </main>
    </div>
  );
}
