/**
 * CONTENT ENHANCEMENT API ENDPOINT
 *
 * POST /api/rewrite/enhance - Enhance article with improved title, excerpt, and suggestions
 */

export const runtime = 'edge';

import { NextRequest, NextResponse } from 'next/server';
import { createContentRewriterIntegration } from '@/lib/services/content-rewriter.integration';

export const runtime = 'edge';

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

    if (!body.noticiaId) {
      return NextResponse.json(
        { error: 'noticiaId is required' },
        { status: 400 }
      );
    }

    const rewriter = getRewriterService();
    const enhancements = await rewriter.enhanceNoticia(body.noticiaId);

    return NextResponse.json({
      success: true,
      enhancements,
    });
  } catch (error) {
    console.error('Enhancement error:', error);

    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Failed to enhance article',
      },
      { status: 500 }
    );
  }
}
