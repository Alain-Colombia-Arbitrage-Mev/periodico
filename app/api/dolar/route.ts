import { NextResponse } from 'next/server';
import { dolarService } from '@/lib/services/dolar.service';

export const runtime = 'edge';
export const dynamic = 'force-dynamic';
export const revalidate = 300; // Revalidar cada 5 minutos

/**
 * GET /api/dolar
 * Obtiene las cotizaciones actuales del dólar
 */
export async function GET() {
  try {
    const cotizaciones = await dolarService.getCotizaciones();

    return NextResponse.json(
      {
        success: true,
        data: cotizaciones,
        timestamp: new Date().toISOString(),
      },
      {
        status: 200,
        headers: {
          'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=600',
        },
      }
    );
  } catch (error) {
    console.error('Error en /api/dolar:', error);

    return NextResponse.json(
      {
        success: false,
        error: 'Error al obtener cotizaciones',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
