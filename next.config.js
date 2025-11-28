/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Skip trailing slash for Cloudflare Pages
  trailingSlash: false,

  // Suppress Cloudflare cookie warnings in development
  onDemandEntries: {
    maxInactiveAge: 25 * 1000,
    pagesBufferLength: 2,
  },

  // Force complete rebuild - no cache
  generateBuildId: async () => {
    return `build-${Date.now()}-complete-rebuild`;
  },
  
  // Image Optimization - unoptimized for Cloudflare Pages
  images: {
    unoptimized: true, // Required for Cloudflare Pages
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'source.unsplash.com',
        pathname: '/**',
      },
      // Supabase Storage (fuente principal de imágenes)
      {
        protocol: 'https',
        hostname: 'dnacsmoubqrzpbvjhary.supabase.co',
        pathname: '/**',
      },
      // Placeholder para artículos sin imagen
      {
        protocol: 'https',
        hostname: 'via.placeholder.com',
        pathname: '/**',
      },
      // Sitios de noticias argentinos
      {
        protocol: 'https',
        hostname: 'www.cronista.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'www.lanacion.com.ar',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'bucket1.glanacion.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'bucket2.glanacion.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'bucket3.glanacion.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'resizer.glanacion.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'www.clarin.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'cloudfront-us-east-1.images.arcpublishing.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'www.infobae.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'www.perfil.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'www.ambito.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'www.pagina12.com.ar',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'cdn.pagina12.com.ar',
        pathname: '/**',
      },
      // CDNs comunes
      {
        protocol: 'https',
        hostname: '*.cloudfront.net',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'cloudinary.com',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: '*.cloudinary.com',
        pathname: '/**',
      },
    ],
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
    dangerouslyAllowSVG: true,
    contentDispositionType: 'inline',
  },
  
  // Compression
  compress: true,
  
  // Performance
  poweredByHeader: false,
  
  // Headers for Security and Performance
  async headers() {
    return [
      // Static assets - allow Next.js to set correct MIME types
      {
        source: '/_next/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      // Security headers for HTML pages only (exclude static assets)
      {
        source: '/((?!_next|api).*)',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
        ],
      },
      {
        source: '/fonts/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
      {
        source: '/_next/image',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};

export default nextConfig;
