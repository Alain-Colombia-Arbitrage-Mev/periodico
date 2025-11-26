'use client';

import Image from 'next/image';
import { useState } from 'react';
import { getSupabaseImageUrl, isSupabaseImage } from '@/lib/utils';
import { validateImageUrl, getBlurDataURL, isSupabaseImage as isSupabaseImg } from '@/lib/utils/image-optimizer';

interface NewsImageProps {
  src: string;
  alt: string;
  fill?: boolean;
  width?: number;
  height?: number;
  className?: string;
  sizes?: string;
  priority?: boolean;
}

export default function NewsImage({
  src,
  alt,
  fill = false,
  width,
  height,
  className = '',
  sizes,
  priority = false,
}: NewsImageProps) {
  // Validate and clean image URL immediately
  const validatedSrc = validateImageUrl(src);
  const [imgSrc, setImgSrc] = useState(validatedSrc);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Fallback image
  const fallbackSrc = getBlurDataURL();

  const handleError = () => {
    if (!hasError) {
      setHasError(true);
      setImgSrc(fallbackSrc);
      setIsLoading(false);
    }
  };

  const handleLoad = () => {
    setIsLoading(false);
  };

  // Procesar URL usando utilidad centralizada
  let cleanSrc = getSupabaseImageUrl(imgSrc);

  // Si la URL contiene un data URI malformado de Supabase, extraerlo
  if (cleanSrc.includes('data:image/svg+xml')) {
    const dataUriMatch = cleanSrc.match(/data:image\/svg\+xml[^)]+/);
    if (dataUriMatch) {
      cleanSrc = dataUriMatch[0].replace(/&amp;/g, '&');
    }
  }

  // Si es externa con query params y no es de Supabase, limpiar
  if (cleanSrc.includes('?') && !isSupabaseImage(cleanSrc) && !cleanSrc.startsWith('data:')) {
    cleanSrc = cleanSrc.split('?')[0];
  }

  // Detectar si es data URI
  const isDataUri = cleanSrc.startsWith('data:');

  // Determinar si la imagen es de Supabase Storage (optimizada) o externa (no optimizada)
  const shouldOptimize = isSupabaseImage(cleanSrc) && !isDataUri;

  // Para data URIs, usar <img> nativo en lugar de Next.js Image
  if (isDataUri) {
    if (fill) {
      return (
        <div className="absolute inset-0">
          {isLoading && (
            <div className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 animate-pulse" />
          )}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={cleanSrc}
            alt={alt}
            className={`${className} w-full h-full object-cover ${
              isLoading ? 'opacity-0' : 'opacity-100 transition-opacity duration-300'
            }`}
            onError={handleError}
            onLoad={handleLoad}
          />
        </div>
      );
    }

    return (
      <div className="relative" style={{ width, height }}>
        {isLoading && width && height && (
          <div
            className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 animate-pulse rounded"
            style={{ width, height }}
          />
        )}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={cleanSrc}
          alt={alt}
          width={width}
          height={height}
          className={`${className} ${isLoading ? 'opacity-0' : 'opacity-100 transition-opacity duration-300'}`}
          onError={handleError}
          onLoad={handleLoad}
        />
      </div>
    );
  }

  // Para URLs normales, usar Next.js Image con unoptimized para imágenes externas
  if (fill) {
    return (
      <>
        {/* Skeleton loading */}
        {isLoading && (
          <div className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 animate-pulse" />
        )}

        <Image
          src={cleanSrc}
          alt={alt}
          fill
          className={`${className} ${isLoading ? 'opacity-0' : 'opacity-100 transition-opacity duration-300'}`}
          sizes={sizes}
          priority={priority}
          onError={handleError}
          onLoad={handleLoad}
          unoptimized={!shouldOptimize}
        />
      </>
    );
  }

  return (
    <div className="relative">
      {/* Skeleton loading */}
      {isLoading && width && height && (
        <div
          className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 animate-pulse rounded"
          style={{ width, height }}
        />
      )}

      <Image
        src={cleanSrc}
        alt={alt}
        width={width || 800}
        height={height || 400}
        className={`${className} ${isLoading ? 'opacity-0' : 'opacity-100 transition-opacity duration-300'}`}
        sizes={sizes}
        priority={priority}
        onError={handleError}
        onLoad={handleLoad}
        unoptimized={!shouldOptimize}
      />
    </div>
  );
}









