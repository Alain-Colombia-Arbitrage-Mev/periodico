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

    // Incrementar vistas usando la función RPC
    const { error } = await supabaseHelpers.incrementViews(id);

    if (error) {
      console.error('Error incrementing views:', error);
      // No retornamos error al cliente - las vistas no son críticas
      return NextResponse.json({ success: true, cached: true });
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error in views API:', error);
    // Silently fail - views are not critical
    return NextResponse.json({ success: true, cached: true });
  }
}
