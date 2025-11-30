/**
 * CONTENT REWRITING API ENDPOINT
 *
 * POST /api/rewrite - Rewrite a single article
 * POST /api/rewrite/batch - Batch rewrite articles
 * GET /api/rewrite/jobs/:id - Get job status
 * GET /api/rewrite/stats - Get rewriting statistics
 */

export const runtime = 'edge';

import { NextRequest, NextResponse } from 'next/server';
import { createContentRewriterIntegration } from '@/lib/services/content-rewriter.integration';

export const runtime = 'edge';

// Initialize the rewriter service
function getRewriterService() {
  const apiKey = process.env.OPENROUTER_API_KEY;

  if (!apiKey) {
    throw new Error('OPENROUTER_API_KEY not configured');
  }

  return createContentRewriterIntegration(apiKey);
}

// POST /api/rewrite - Rewrite single article
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate request
    if (!body.noticiaId) {
      return NextResponse.json(
        { error: 'noticiaId is required' },
        { status: 400 }
      );
    }

    const rewriter = getRewriterService();

    const job = await rewriter.rewriteNoticia({
      noticiaId: body.noticiaId,
      style: body.style || 'formal',
      tone: body.tone || 'neutral',
      length: body.length || 'same',
      updateOriginal: body.updateOriginal || false,
      generateNewHeadline: body.generateNewHeadline || false,
      model: body.model,
    });

    return NextResponse.json({
      success: true,
      job,
    });
  } catch (error) {
    console.error('Rewrite error:', error);

    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Failed to rewrite article',
      },
      { status: 500 }
    );
  }
}

// GET /api/rewrite?jobId=xxx - Get job status
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const jobId = searchParams.get('jobId');

    if (!jobId) {
      return NextResponse.json(
        { error: 'jobId parameter is required' },
        { status: 400 }
      );
    }

    const rewriter = getRewriterService();
    const job = rewriter.getJob(jobId);

    if (!job) {
      return NextResponse.json(
        { error: 'Job not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      job,
    });
  } catch (error) {
    console.error('Get job error:', error);

    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Failed to get job',
      },
      { status: 500 }
    );
  }
}
