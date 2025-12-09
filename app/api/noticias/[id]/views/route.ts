import { NextRequest, NextResponse } from 'next/server';
import { supabaseHelpers } from '@/lib/supabase';

export const runtime = 'edge';

// POST /api/noticias/[id]/views - Incrementar vistas
export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;

    if (!id) {
      return NextResponse.json(
        { error: 'ID de noticia requerido' },
        { status: 400 }
      );
    }

    // Incrementar vistas
    const { data, error } = await supabaseHelpers.incrementViews(id);

    if (error) {
      console.error('Error incrementing views:', error);
      return NextResponse.json({ 
        success: false, 
        error: error.message,
        id 
      }, { status: 500 });
    }

    return NextResponse.json({ success: true, id });
  } catch (error) {
    console.error('Error in views API:', error);
    return NextResponse.json({ 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 });
  }
}

// GET /api/noticias/[id]/views - Obtener vistas actuales (para testing)
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    
    const { data, error } = await supabaseHelpers.getNoticiaById(id);
    
    if (error || !data) {
      return NextResponse.json({ error: 'Noticia no encontrada' }, { status: 404 });
    }
    
    return NextResponse.json({ 
      id,
      views: data.views,
      title: data.title
    });
  } catch (error) {
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : 'Unknown error' 
    }, { status: 500 });
  }
}
