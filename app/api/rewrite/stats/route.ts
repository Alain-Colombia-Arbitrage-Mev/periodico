/**
 * REWRITING STATS API ENDPOINT
 *
 * GET /api/rewrite/stats - Get rewriting statistics
 */

import { NextRequest, NextResponse } from 'next/server';
import { createContentRewriterIntegration } from '@/lib/services/content-rewriter.integration';

function getRewriterService() {
  const apiKey = process.env.OPENROUTER_API_KEY;

  if (!apiKey) {
    throw new Error('OPENROUTER_API_KEY not configured');
  }

  return createContentRewriterIntegration(apiKey);
}

export async function GET(request: NextRequest) {
  try {
    const rewriter = getRewriterService();
    const stats = rewriter.getStats();

    return NextResponse.json({
      success: true,
      stats,
    });
  } catch (error) {
    console.error('Get stats error:', error);

    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Failed to get stats',
      },
      { status: 500 }
    );
  }
}
