/**
 * API ROUTE - NOTICIAS V1
 * Serverless-optimized with caching and error handling
 */

import { NextRequest, NextResponse } from 'next/server';
import { noticiaService } from '@/lib/services/noticia.service';
import { handleError } from '@/lib/utils';

export const runtime = 'edge';

// ============================================
// GET /api/v1/noticias
// ============================================
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    
    const category = searchParams.get('category') || undefined;
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '20');

    // Validate parameters
    if (page < 1 || limit < 1 || limit > 100) {
      return NextResponse.json(
        { error: 'Invalid pagination parameters' },
        { status: 400 }
      );
    }

    const result = await noticiaService.getAllNoticias({
      category,
      page,
      limit,
    });

    return NextResponse.json({
      success: true,
      data: result.data,
      pagination: {
        page: result.page,
        limit,
        total: result.total,
        totalPages: result.totalPages,
      },
    }, {
      headers: {
        'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=600',
      },
    });
  } catch (error) {
    const { message, code } = handleError(error);
    return NextResponse.json(
      { error: message, code },
      { status: 500 }
    );
  }
}

// ============================================
// POST /api/v1/noticias
// ============================================
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate required fields
    if (!body.title || !body.category || !body.excerpt) {
      return NextResponse.json(
        { error: 'Missing required fields: title, category, excerpt' },
        { status: 400 }
      );
    }

    const noticia = await noticiaService.createNoticia(body);

    return NextResponse.json({
      success: true,
      data: noticia,
      message: 'Noticia created successfully',
    }, { status: 201 });
  } catch (error) {
    const { message, code } = handleError(error);
    return NextResponse.json(
      { error: message, code },
      { status: 500 }
    );
  }
}

// ============================================
// OPTIONS - CORS
// ============================================
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}

