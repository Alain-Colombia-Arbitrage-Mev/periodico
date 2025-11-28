export const runtime = 'edge';

'use client';

import { use, useEffect, useState } from 'react';
import { notFound } from 'next/navigation';
import ArticlePage from '@/components/ArticlePage';
import { supabaseHelpers } from '@/lib/supabase';

interface PageProps {
  params: Promise<{
    categoria: string;
    slug: string;
  }>;
}

interface Noticia {
  id: string;
  title: string;
  subtitle?: string;
  excerpt: string;
  content: string;
  image_url: string;
  audio_url?: string;
  video_url?: string;
  slug: string;
  published_at: string;
  updated_at?: string;
  views: number;
  is_breaking: boolean;
  source_type: number;
  source_url?: string;
  categorias: {
    name: string;
    slug: string;
    color: string;
  };
}

export default function ArticleDetailPage({ params }: PageProps) {
  // Unwrap params Promise for Next.js 15+
  const { categoria, slug } = use(params);

  const [noticia, setNoticia] = useState<Noticia | null>(null);
  const [relatedArticles, setRelatedArticles] = useState<any[]>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [notFoundError, setNotFoundError] = useState(false);

  useEffect(() => {
    async function fetchArticle() {
      try {
        // Fetch the article by slug
        const { data, error } = await supabaseHelpers.getNoticiaBySlug(slug);

        if (error || !data || data.length === 0) {
          setNotFoundError(true);
          setLoading(false);
          return;
        }

        const article = data[0] as Noticia;

        // Verify the category matches
        if (article.categorias?.slug !== categoria) {
          setNotFoundError(true);
          setLoading(false);
          return;
        }

        setNoticia(article);

        // Fetch tags for this article
        const { data: tagsData } = await supabaseHelpers.getNoticiasTags(article.id);
        const fetchedTags = tagsData?.map((t: any) => t.tags.name) || [];
        setTags(fetchedTags);

        // Fetch related articles from the same category
        const { data: relatedData } = await supabaseHelpers.getNoticias({
          status: 'published',
          category: categoria,
          limit: 6
        });

        if (relatedData) {
          // Prioritize articles with shared tags
          const filtered = relatedData
            .filter((n: any) => n.id !== article.id)
            .map((n: any) => ({
              id: n.id,
              title: n.title,
              imageUrl: n.image_url,
              category: n.categorias?.name || 'Noticias',
              categorySlug: n.categorias?.slug || 'noticias',
              slug: n.slug,
            }))
            .slice(0, 4);

          setRelatedArticles(filtered);
        }
      } catch (error) {
        console.error('Error fetching article:', error);
        setNotFoundError(true);
      } finally {
        setLoading(false);
      }
    }

    fetchArticle();
  }, [slug, categoria]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg">Cargando artículo...</p>
      </div>
    );
  }

  if (notFoundError || !noticia) {
    notFound();
  }

  // Convert Noticia to Article format for ArticlePage component
  const article = {
    id: noticia.id,
    title: noticia.title,
    subtitle: noticia.subtitle,
    excerpt: noticia.excerpt,
    content: noticia.content || `<p>${noticia.excerpt}</p><p>Esta es una noticia en desarrollo. Estamos trabajando para proporcionarle toda la información relevante sobre este tema.</p>`,
    imageUrl: noticia.image_url,
    audioUrl: noticia.audio_url,
    videoUrl: noticia.video_url,
    category: noticia.categorias?.name || 'Noticias',
    categorySlug: noticia.categorias?.slug || 'noticias',
    publishedAt: new Date(noticia.published_at),
    updatedAt: new Date(noticia.updated_at || noticia.published_at),
    views: noticia.views,
    tags: tags,
    readingTime: Math.ceil(noticia.content?.split(' ').length / 200) || 3,
  };

  return <ArticlePage article={article} relatedArticles={relatedArticles} />;
}
