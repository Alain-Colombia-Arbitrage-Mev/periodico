import { notFound } from 'next/navigation';
import ArticlePage from '@/components/ArticlePage';
import { supabaseHelpers } from '@/lib/supabase';

export const runtime = 'edge';

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

export default async function ArticleDetailPage({ params }: PageProps) {
  const { categoria, slug } = await params;

  // Fetch the article by slug
  const { data, error } = await supabaseHelpers.getNoticiaBySlug(slug);

  if (error || !data || data.length === 0) {
    notFound();
  }

  const noticia = data[0] as Noticia;

  // Verify the category matches
  if (noticia.categorias?.slug !== categoria) {
    notFound();
  }

  // Fetch tags for this article
  const { data: tagsData } = await supabaseHelpers.getNoticiasTags(noticia.id);
  const tags = tagsData?.map((t: any) => t.tags.name) || [];

  // Fetch related articles from the same category
  const { data: relatedData } = await supabaseHelpers.getNoticias({
    status: 'published',
    category: categoria,
    limit: 6
  });

  const relatedArticles = relatedData
    ? relatedData
        .filter((n: any) => n.id !== noticia.id)
        .map((n: any) => ({
          id: n.id,
          title: n.title,
          imageUrl: n.image_url,
          category: n.categorias?.name || 'Noticias',
          categorySlug: n.categorias?.slug || 'noticias',
          slug: n.slug,
        }))
        .slice(0, 4)
    : [];

  // Convert Noticia to Article format for ArticlePage component
  const article = {
    id: noticia.id,
    title: noticia.title,
    subtitle: noticia.subtitle,
    excerpt: noticia.excerpt,
    content: noticia.content || `<p>${noticia.excerpt}</p><p>Esta es una noticia en desarrollo. Estamos trabajando para proporcionarle toda la información relevante sobre este tema.</p>`,
    imageUrl: noticia.image_url,
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
