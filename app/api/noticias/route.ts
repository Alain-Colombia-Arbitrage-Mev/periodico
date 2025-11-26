import { NextRequest, NextResponse } from 'next/server';
import { supabaseHelpers } from '@/lib/supabase';

// Enable caching at the edge
export const runtime = 'edge';
export const revalidate = 60; // Revalidate every 60 seconds

// GET /api/noticias - Obtener todas las noticias
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const category = searchParams.get('category') || undefined;
    const status = searchParams.get('status') || undefined;
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100); // Max 100
    const offset = parseInt(searchParams.get('offset') || '0');

    const { data, error } = await supabaseHelpers.getNoticias({
      category,
      status,
      limit,
      offset,
    });

    if (error) {
      console.error('Supabase error:', error);
      return NextResponse.json(
        { error: error.message, success: false },
        {
          status: 500,
          headers: {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
          },
        }
      );
    }

    // Set cache headers for successful responses
    return NextResponse.json(
      {
        success: true,
        data,
        count: data?.length || 0,
      },
      {
        headers: {
          'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
          'Content-Type': 'application/json',
        },
      }
    );
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Error interno del servidor', success: false },
      {
        status: 500,
        headers: {
          'Cache-Control': 'no-cache',
        },
      }
    );
  }
}

// POST /api/noticias - Crear nueva noticia
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validación básica
    if (!body.title || !body.excerpt || !body.content) {
      return NextResponse.json(
        { error: 'Faltan campos requeridos' },
        { status: 400 }
      );
    }

    // Generar slug del título
    const slug = body.title
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');

    const noticiaData = {
      ...body,
      slug: body.slug || slug,
      views: 0,
      status: body.status || 'draft',
      is_breaking: body.is_breaking || false,
      source_type: body.source_type ?? 1, // Default: 1 = manual, 0 = scraper
      source_url: body.source_url || null,
      published_at: body.status === 'published' ? new Date().toISOString() : null,
    };

    const { data, error } = await supabaseHelpers.createNoticia(noticiaData);

    if (error) {
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      data,
      message: 'Noticia creada exitosamente',
    }, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: 'Error al crear noticia' },
      { status: 500 }
    );
  }
}

