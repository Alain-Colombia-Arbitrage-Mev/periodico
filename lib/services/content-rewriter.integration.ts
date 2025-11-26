/**
 * CONTENT REWRITER INTEGRATION SERVICE
 *
 * Integrates OpenRouter with the existing noticia service
 * for automated content rewriting workflows
 */

import { createOpenRouterService } from './openrouter.service';
import { noticiaService } from './noticia.service';
import type { Noticia } from '../database';

// ============================================
// TYPES
// ============================================

export interface RewriteJobConfig {
  noticiaId: string;
  style?: 'formal' | 'casual' | 'investigative' | 'opinion';
  tone?: 'neutral' | 'critical' | 'supportive';
  length?: 'shorter' | 'same' | 'longer';
  updateOriginal?: boolean;
  generateNewHeadline?: boolean;
  model?: string;
}

export interface RewriteJob {
  id: string;
  noticiaId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  config: RewriteJobConfig;
  result?: {
    originalTitle: string;
    rewrittenTitle?: string;
    originalContent: string;
    rewrittenContent: string;
    tokensUsed: number;
    cost: number;
    model: string;
  };
  error?: string;
  createdAt: string;
  completedAt?: string;
}

export interface BatchRewriteConfig {
  category?: string;
  limit?: number;
  style?: 'formal' | 'casual' | 'investigative' | 'opinion';
  tone?: 'neutral' | 'critical' | 'supportive';
  model?: string;
}

// ============================================
// JOB QUEUE MANAGER
// ============================================

class RewriteJobQueue {
  private static instance: RewriteJobQueue;
  private jobs: Map<string, RewriteJob> = new Map();
  private processing = false;

  static getInstance(): RewriteJobQueue {
    if (!RewriteJobQueue.instance) {
      RewriteJobQueue.instance = new RewriteJobQueue();
    }
    return RewriteJobQueue.instance;
  }

  addJob(job: RewriteJob): void {
    this.jobs.set(job.id, job);
    this.processQueue();
  }

  getJob(id: string): RewriteJob | undefined {
    return this.jobs.get(id);
  }

  getAllJobs(): RewriteJob[] {
    return Array.from(this.jobs.values());
  }

  private async processQueue(): Promise<void> {
    if (this.processing) return;

    this.processing = true;

    while (true) {
      const pendingJob = Array.from(this.jobs.values()).find(
        (job) => job.status === 'pending'
      );

      if (!pendingJob) break;

      await this.processJob(pendingJob);
    }

    this.processing = false;
  }

  private async processJob(job: RewriteJob): Promise<void> {
    job.status = 'processing';
    this.jobs.set(job.id, { ...job });

    // Job processing will be handled by ContentRewriterIntegration
  }
}

// ============================================
// CONTENT REWRITER INTEGRATION
// ============================================

export class ContentRewriterIntegration {
  private static instance: ContentRewriterIntegration;
  private openRouter: ReturnType<typeof createOpenRouterService>;
  private jobQueue: RewriteJobQueue;

  private constructor(apiKey: string) {
    this.openRouter = createOpenRouterService(apiKey);
    this.jobQueue = RewriteJobQueue.getInstance();
  }

  static getInstance(apiKey?: string): ContentRewriterIntegration {
    if (!ContentRewriterIntegration.instance) {
      if (!apiKey) {
        throw new Error('API key required for first initialization');
      }
      ContentRewriterIntegration.instance = new ContentRewriterIntegration(apiKey);
    }
    return ContentRewriterIntegration.instance;
  }

  // ============================================
  // SINGLE ARTICLE REWRITING
  // ============================================

  async rewriteNoticia(config: RewriteJobConfig): Promise<RewriteJob> {
    const jobId = this.generateJobId();

    const job: RewriteJob = {
      id: jobId,
      noticiaId: config.noticiaId,
      status: 'pending',
      config,
      createdAt: new Date().toISOString(),
    };

    this.jobQueue.addJob(job);

    try {
      // Fetch the noticia
      const noticia = await noticiaService.getNoticiaById(config.noticiaId);

      if (!noticia) {
        throw new Error(`Noticia ${config.noticiaId} not found`);
      }

      job.status = 'processing';

      // Rewrite content
      const rewriteResult = await this.openRouter.rewritingService.rewriteNewsArticle(
        noticia.title,
        noticia.content || noticia.excerpt,
        {
          style: config.style,
          tone: config.tone,
          length: config.length,
          preserveFacts: true,
          model: config.model,
        }
      );

      let rewrittenTitle = noticia.title;

      // Generate new headline if requested
      if (config.generateNewHeadline) {
        const headlineResult = await this.openRouter.rewritingService.generateHeadline(
          rewriteResult.rewrittenText,
          {
            style: config.style === 'formal' ? 'professional' : config.style as any,
            maxLength: 80,
            includeSubtitle: true,
          }
        );

        rewrittenTitle = headlineResult.headline;
      }

      // Update job result
      job.result = {
        originalTitle: noticia.title,
        rewrittenTitle: config.generateNewHeadline ? rewrittenTitle : undefined,
        originalContent: noticia.content || noticia.excerpt,
        rewrittenContent: rewriteResult.rewrittenText,
        tokensUsed: rewriteResult.tokensUsed,
        cost: rewriteResult.cost,
        model: rewriteResult.model,
      };

      // Update the original noticia if requested
      if (config.updateOriginal) {
        await noticiaService.updateNoticia(config.noticiaId, {
          content: rewriteResult.rewrittenText,
          ...(config.generateNewHeadline ? { title: rewrittenTitle } : {}),
        });
      }

      job.status = 'completed';
      job.completedAt = new Date().toISOString();

      this.jobQueue.addJob(job);

      return job;
    } catch (error) {
      job.status = 'failed';
      job.error = error instanceof Error ? error.message : 'Unknown error';
      job.completedAt = new Date().toISOString();

      this.jobQueue.addJob(job);

      throw error;
    }
  }

  // ============================================
  // BATCH REWRITING
  // ============================================

  async batchRewrite(config: BatchRewriteConfig): Promise<RewriteJob[]> {
    // Fetch noticias
    const noticias = await noticiaService.getNoticiasByCategory(
      config.category || '',
      config.limit || 10
    );

    const jobs: Promise<RewriteJob>[] = [];

    for (const noticia of noticias) {
      const jobConfig: RewriteJobConfig = {
        noticiaId: noticia.id,
        style: config.style,
        tone: config.tone,
        updateOriginal: false, // Don't auto-update in batch
        model: config.model,
      };

      jobs.push(this.rewriteNoticia(jobConfig));
    }

    return Promise.all(jobs);
  }

  // ============================================
  // CONTENT ENHANCEMENT
  // ============================================

  async enhanceNoticia(noticiaId: string): Promise<{
    improvedTitle: string;
    improvedExcerpt: string;
    suggestions: string[];
  }> {
    const noticia = await noticiaService.getNoticiaById(noticiaId);

    if (!noticia) {
      throw new Error(`Noticia ${noticiaId} not found`);
    }

    // Generate improved headline
    const headlineResult = await this.openRouter.rewritingService.generateHeadline(
      noticia.content || noticia.excerpt,
      {
        style: 'professional',
        maxLength: 80,
        includeSubtitle: true,
      }
    );

    // Generate improved excerpt
    const improvedExcerpt = await this.openRouter.rewritingService.summarizeArticle(
      noticia.content || noticia.excerpt,
      150
    );

    // Generate editorial suggestions
    const suggestions = await this.generateEditorialSuggestions(noticia);

    return {
      improvedTitle: headlineResult.headline,
      improvedExcerpt,
      suggestions,
    };
  }

  private async generateEditorialSuggestions(noticia: Noticia): Promise<string[]> {
    const prompt = `As a senior editor reviewing this Argentine political news article, provide 3-5 specific editorial suggestions to improve it:

TITLE: ${noticia.title}
CONTENT: ${(noticia.content || noticia.excerpt).substring(0, 1000)}

Return suggestions as JSON array: ["suggestion 1", "suggestion 2", ...]`;

    const response = await this.openRouter.client.chat({
      model: 'meta-llama/llama-4-maverick',
      messages: [
        {
          role: 'system',
          content: 'You are a senior news editor for Argentine political journalism.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.8,
      max_tokens: 500,
      response_format: { type: 'json_object' },
    });

    const result = JSON.parse(response.choices[0].message.content);
    return result.suggestions || [];
  }

  // ============================================
  // MONITORING & STATS
  // ============================================

  getJobs(): RewriteJob[] {
    return this.jobQueue.getAllJobs();
  }

  getJob(id: string): RewriteJob | undefined {
    return this.jobQueue.getJob(id);
  }

  getStats() {
    const jobs = this.jobQueue.getAllJobs();

    return {
      totalJobs: jobs.length,
      completed: jobs.filter((j) => j.status === 'completed').length,
      failed: jobs.filter((j) => j.status === 'failed').length,
      pending: jobs.filter((j) => j.status === 'pending').length,
      processing: jobs.filter((j) => j.status === 'processing').length,
      openRouterStats: this.openRouter.client.getStats(),
    };
  }

  // ============================================
  // UTILITIES
  // ============================================

  private generateJobId(): string {
    return `job_${Date.now()}_${Math.random().toString(36).substring(7)}`;
  }
}

// ============================================
// EXPORT FACTORY
// ============================================

export function createContentRewriterIntegration(apiKey: string) {
  return ContentRewriterIntegration.getInstance(apiKey);
}
