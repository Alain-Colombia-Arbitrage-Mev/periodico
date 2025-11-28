export const runtime = 'edge';

import { Metadata } from 'next';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowLeft, Tag as TagIcon, Eye } from 'lucide-react';
import { supabaseHelpers } from '@/lib/supabase';
import { formatDistanceToNow } from 'date-fns';
import { es } from 'date-fns/locale';

type Props = {
  params: Promise<{ tag: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { tag } = await params;
  const decodedTag = decodeURIComponent(tag.replace(/-/g, ' '));

  return {
    title: `Noticias sobre ${decodedTag} | Política Argentina`,
    description: `Todas las noticias relacionadas con ${decodedTag}. Mantente informado con nuestra cobertura completa.`,
  };
}

export default async function TagPage({ params }: Props) {
  const { tag } = await params;
  const decodedTag = decodeURIComponent(tag.replace(/-/g, ' '));

  // Obtener noticias que contengan este tag
  const { data: noticias } = await supabaseHelpers.getNoticiasByTag(decodedTag);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Volver al inicio</span>
          </Link>

          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 bg-blue-100 rounded-lg">
              <TagIcon className="w-6 h-6 text-blue-600" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900">
              #{decodedTag}
            </h1>
          </div>

          <p className="text-gray-600 text-lg">
            {noticias?.length || 0} {noticias?.length === 1 ? 'noticia encontrada' : 'noticias encontradas'}
          </p>
        </div>

        {/* Noticias */}
        {noticias && noticias.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {noticias.map((noticia: any) => (
              <Link
                key={noticia.id}
                href={`/${noticia.categorias.slug}/${noticia.slug}`}
                className="group bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
              >
                <div className="relative h-48">
                  <Image
                    src={noticia.image_url}
                    alt={noticia.title}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-300"
                    sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                  />
                </div>
                <div className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-semibold uppercase px-2 py-1 rounded" style={{ backgroundColor: noticia.categorias.color + '20', color: noticia.categorias.color }}>
                      {noticia.categorias.name}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
                    {noticia.title}
                  </h3>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {noticia.excerpt}
                  </p>
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <time>
                      {formatDistanceToNow(new Date(noticia.published_at), {
                        addSuffix: true,
                        locale: es
                      })}
                    </time>
                    <span className="flex items-center gap-1">
                      <Eye className="w-3 h-3" />
                      {noticia.views.toLocaleString()}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
            <TagIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No hay noticias con este tag
            </h3>
            <p className="text-gray-600 mb-6">
              Aún no se han publicado noticias con el tag &quot;{decodedTag}&quot;
            </p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Explorar todas las noticias
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
