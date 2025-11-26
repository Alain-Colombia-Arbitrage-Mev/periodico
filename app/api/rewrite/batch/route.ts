/**
 * BATCH REWRITING API ENDPOINT
 *
 * POST /api/rewrite/batch - Batch rewrite multiple articles
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

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const rewriter = getRewriterService();

    const jobs = await rewriter.batchRewrite({
      category: body.category,
      limit: body.limit || 10,
      style: body.style || 'formal',
      tone: body.tone || 'neutral',
      model: body.model,
    });

    return NextResponse.json({
      success: true,
      jobs,
      count: jobs.length,
    });
  } catch (error) {
    console.error('Batch rewrite error:', error);

    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Failed to batch rewrite',
      },
      { status: 500 }
    );
  }
}
