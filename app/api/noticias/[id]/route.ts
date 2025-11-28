import { NextRequest, NextResponse } from 'next/server';
import { supabaseHelpers } from '@/lib/supabase';

export const runtime = 'edge';

// GET /api/noticias/[id] - Obtener una noticia por ID
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const { data, error } = await supabaseHelpers.getNoticiaById(id);

    if (error) {
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      );
    }

    if (!data) {
      return NextResponse.json(
        { error: 'Noticia no encontrada' },
        { status: 404 }
      );
    }

    // Incrementar vistas
    await supabaseHelpers.incrementViews(id);

    return NextResponse.json({
      success: true,
      data,
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Error al obtener noticia' },
      { status: 500 }
    );
  }
}

// PUT /api/noticias/[id] - Actualizar una noticia
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const body = await request.json();

    // Si se está publicando, agregar fecha de publicación
    if (body.status === 'published' && !body.published_at) {
      body.published_at = new Date().toISOString();
    }

    const { data, error } = await supabaseHelpers.updateNoticia(id, body);

    if (error) {
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      data,
      message: 'Noticia actualizada exitosamente',
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Error al actualizar noticia' },
      { status: 500 }
    );
  }
}

// DELETE /api/noticias/[id] - Eliminar una noticia
export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const { error } = await supabaseHelpers.deleteNoticia(id);

    if (error) {
      return NextResponse.json(
        { error: error.message },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      message: 'Noticia eliminada exitosamente',
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Error al eliminar noticia' },
      { status: 500 }
    );
  }
}

