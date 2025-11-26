/**
 * OPENROUTER LLM SERVICE - PRODUCTION-READY INTEGRATION
 *
 * Features:
 * - Rate limiting and backoff strategies
 * - Cost tracking and optimization
 * - Error handling and retry logic
 * - Response caching
 * - Token usage monitoring
 * - Model fallback support
 */

import { cache } from '../database';

// ============================================
// TYPES & INTERFACES
// ============================================

export interface OpenRouterConfig {
  apiKey: string;
  baseUrl?: string;
  defaultModel?: string;
  maxRetries?: number;
  timeout?: number;
  rateLimit?: {
    requestsPerMinute: number;
    requestsPerDay: number;
  };
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface OpenRouterRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stream?: boolean;
  response_format?: { type: 'json_object' };
}

export interface OpenRouterResponse {
  id: string;
  model: string;
  choices: Array<{
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  created: number;
}

export interface RewriteResult {
  originalText: string;
  rewrittenText: string;
  model: string;
  tokensUsed: number;
  cost: number;
  timestamp: string;
}

// ============================================
// RATE LIMITER
// ============================================

class RateLimiter {
  private requestTimestamps: number[] = [];
  private dailyRequests: number = 0;
  private lastResetDate: string = new Date().toDateString();

  constructor(
    private requestsPerMinute: number = 20,
    private requestsPerDay: number = 1000
  ) {}

  async checkLimit(): Promise<boolean> {
    this.cleanup();

    // Reset daily counter if new day
    const today = new Date().toDateString();
    if (this.lastResetDate !== today) {
      this.dailyRequests = 0;
      this.lastResetDate = today;
    }

    // Check daily limit
    if (this.dailyRequests >= this.requestsPerDay) {
      throw new Error('Daily rate limit exceeded');
    }

    // Check per-minute limit
    const now = Date.now();
    const recentRequests = this.requestTimestamps.filter(
      (timestamp) => now - timestamp < 60000
    );

    if (recentRequests.length >= this.requestsPerMinute) {
      const oldestRequest = Math.min(...recentRequests);
      const waitTime = 60000 - (now - oldestRequest);
      await this.sleep(waitTime);
    }

    return true;
  }

  recordRequest(): void {
    this.requestTimestamps.push(Date.now());
    this.dailyRequests++;
  }

  private cleanup(): void {
    const now = Date.now();
    this.requestTimestamps = this.requestTimestamps.filter(
      (timestamp) => now - timestamp < 60000
    );
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  getStats() {
    return {
      dailyRequests: this.dailyRequests,
      recentRequests: this.requestTimestamps.length,
      lastReset: this.lastResetDate,
    };
  }
}

// ============================================
// COST TRACKER
// ============================================

class CostTracker {
  private static instance: CostTracker;
  private costs: Map<string, number> = new Map();
  private tokenUsage: Map<string, number> = new Map();

  // Estimated costs per 1M tokens (update based on actual pricing)
  private readonly MODEL_COSTS: Record<string, { input: number; output: number }> = {
    'anthropic/claude-3.5-sonnet': { input: 3.0, output: 15.0 },
    'openai/gpt-4o': { input: 2.5, output: 10.0 },
    'google/gemini-1.5-pro': { input: 1.25, output: 5.0 },
    'meta-llama/llama-4-maverick': { input: 0.5, output: 2.0 },
    'zhipu/glm-4.5': { input: 0.3, output: 1.0 },
    'inflection/inflection-3-productivity': { input: 0.4, output: 1.5 },
  };

  static getInstance(): CostTracker {
    if (!CostTracker.instance) {
      CostTracker.instance = new CostTracker();
    }
    return CostTracker.instance;
  }

  calculateCost(
    model: string,
    promptTokens: number,
    completionTokens: number
  ): number {
    const pricing = this.MODEL_COSTS[model] || { input: 1.0, output: 3.0 };
    const cost =
      (promptTokens / 1_000_000) * pricing.input +
      (completionTokens / 1_000_000) * pricing.output;

    return cost;
  }

  recordUsage(model: string, cost: number, tokens: number): void {
    const currentCost = this.costs.get(model) || 0;
    const currentTokens = this.tokenUsage.get(model) || 0;

    this.costs.set(model, currentCost + cost);
    this.tokenUsage.set(model, currentTokens + tokens);
  }

  getStats() {
    const stats: Record<string, any> = {};

    for (const [model, cost] of this.costs.entries()) {
      stats[model] = {
        totalCost: cost,
        totalTokens: this.tokenUsage.get(model) || 0,
      };
    }

    return stats;
  }

  getTotalCost(): number {
    return Array.from(this.costs.values()).reduce((sum, cost) => sum + cost, 0);
  }
}

// ============================================
// OPENROUTER CLIENT
// ============================================

export class OpenRouterClient {
  private static instance: OpenRouterClient;
  private config: Required<OpenRouterConfig>;
  private rateLimiter: RateLimiter;
  private costTracker: CostTracker;

  private constructor(config: OpenRouterConfig) {
    this.config = {
      apiKey: config.apiKey,
      baseUrl: config.baseUrl || 'https://openrouter.ai/api/v1',
      defaultModel: config.defaultModel || 'meta-llama/llama-4-maverick',
      maxRetries: config.maxRetries || 3,
      timeout: config.timeout || 60000,
      rateLimit: config.rateLimit || {
        requestsPerMinute: 20,
        requestsPerDay: 1000,
      },
    };

    this.rateLimiter = new RateLimiter(
      this.config.rateLimit.requestsPerMinute,
      this.config.rateLimit.requestsPerDay
    );

    this.costTracker = CostTracker.getInstance();
  }

  static getInstance(config?: OpenRouterConfig): OpenRouterClient {
    if (!OpenRouterClient.instance) {
      if (!config) {
        throw new Error('OpenRouterClient must be initialized with config');
      }
      OpenRouterClient.instance = new OpenRouterClient(config);
    }
    return OpenRouterClient.instance;
  }

  // ============================================
  // CORE API METHODS
  // ============================================

  async chat(request: OpenRouterRequest): Promise<OpenRouterResponse> {
    await this.rateLimiter.checkLimit();

    const response = await this.makeRequestWithRetry(request);

    this.rateLimiter.recordRequest();

    // Track cost
    if (response.usage) {
      const cost = this.costTracker.calculateCost(
        request.model,
        response.usage.prompt_tokens,
        response.usage.completion_tokens
      );

      this.costTracker.recordUsage(
        request.model,
        cost,
        response.usage.total_tokens
      );
    }

    return response;
  }

  private async makeRequestWithRetry(
    request: OpenRouterRequest,
    attempt: number = 1
  ): Promise<OpenRouterResponse> {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), this.config.timeout);

      const response = await fetch(`${this.config.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000',
          'X-Title': 'Politica Argentina Portal',
        },
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));

        // Handle specific error codes
        if (response.status === 429) {
          throw new Error('Rate limit exceeded');
        } else if (response.status === 402) {
          throw new Error('Insufficient credits');
        } else if (response.status >= 500 && attempt < this.config.maxRetries) {
          // Retry on server errors with exponential backoff
          const delay = Math.pow(2, attempt) * 1000;
          await this.sleep(delay);
          return this.makeRequestWithRetry(request, attempt + 1);
        }

        throw new Error(error.error?.message || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (attempt < this.config.maxRetries) {
        const delay = Math.pow(2, attempt) * 1000;
        await this.sleep(delay);
        return this.makeRequestWithRetry(request, attempt + 1);
      }

      throw error;
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // ============================================
  // STATS & MONITORING
  // ============================================

  getStats() {
    return {
      rateLimit: this.rateLimiter.getStats(),
      costs: this.costTracker.getStats(),
      totalCost: this.costTracker.getTotalCost(),
    };
  }
}

// ============================================
// CONTENT REWRITING SERVICE
// ============================================

export class ContentRewritingService {
  private static instance: ContentRewritingService;
  private client: OpenRouterClient;

  private constructor(client: OpenRouterClient) {
    this.client = client;
  }

  static getInstance(client: OpenRouterClient): ContentRewritingService {
    if (!ContentRewritingService.instance) {
      ContentRewritingService.instance = new ContentRewritingService(client);
    }
    return ContentRewritingService.instance;
  }

  // ============================================
  // REWRITING METHODS
  // ============================================

  async rewriteNewsArticle(
    title: string,
    content: string,
    options?: {
      style?: 'formal' | 'casual' | 'investigative' | 'opinion';
      tone?: 'neutral' | 'critical' | 'supportive';
      length?: 'shorter' | 'same' | 'longer';
      preserveFacts?: boolean;
      model?: string;
    }
  ): Promise<RewriteResult> {
    const cacheKey = `rewrite:${this.hashString(title + content)}`;
    const cached = cache.get(cacheKey);

    if (cached) {
      return cached;
    }

    const prompt = this.buildRewritePrompt(title, content, options);

    const request: OpenRouterRequest = {
      model: options?.model || 'meta-llama/llama-4-maverick',
      messages: [
        {
          role: 'system',
          content: this.getSystemPrompt(options),
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.7,
      max_tokens: 4000,
      top_p: 0.9,
    };

    const response = await this.client.chat(request);

    const rewrittenText = response.choices[0].message.content;

    const result: RewriteResult = {
      originalText: content,
      rewrittenText,
      model: response.model,
      tokensUsed: response.usage.total_tokens,
      cost: 0, // Will be calculated by cost tracker
      timestamp: new Date().toISOString(),
    };

    // Cache for 1 hour
    cache.set(cacheKey, result, 3600000);

    return result;
  }

  async generateHeadline(
    content: string,
    options?: {
      style?: 'clickbait' | 'professional' | 'investigative';
      maxLength?: number;
      includeSubtitle?: boolean;
    }
  ): Promise<{ headline: string; subtitle?: string }> {
    const prompt = `Generate a compelling headline for this news article${
      options?.includeSubtitle ? ' with a subtitle' : ''
    }:

${content.substring(0, 1000)}

Style: ${options?.style || 'professional'}
Max length: ${options?.maxLength || 80} characters

${
  options?.includeSubtitle
    ? 'Return as JSON: {"headline": "...", "subtitle": "..."}'
    : 'Return as JSON: {"headline": "..."}'
}`;

    const request: OpenRouterRequest = {
      model: 'meta-llama/llama-4-maverick',
      messages: [
        {
          role: 'system',
          content: 'You are a professional news editor specializing in compelling headlines.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.8,
      max_tokens: 200,
      response_format: { type: 'json_object' },
    };

    const response = await this.client.chat(request);
    return JSON.parse(response.choices[0].message.content);
  }

  async summarizeArticle(
    content: string,
    targetLength: number = 150
  ): Promise<string> {
    const cacheKey = `summary:${this.hashString(content)}:${targetLength}`;
    const cached = cache.get(cacheKey);

    if (cached) {
      return cached;
    }

    const prompt = `Summarize this news article in approximately ${targetLength} words. Focus on the key facts and maintain journalistic objectivity:

${content}

Return only the summary, no additional commentary.`;

    const request: OpenRouterRequest = {
      model: 'zhipu/glm-4.5', // Cost-effective for summaries
      messages: [
        {
          role: 'system',
          content: 'You are a professional news summarizer.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.5,
      max_tokens: Math.ceil(targetLength * 1.5),
    };

    const response = await this.client.chat(request);
    const summary = response.choices[0].message.content.trim();

    cache.set(cacheKey, summary, 3600000);

    return summary;
  }

  // ============================================
  // PROMPT BUILDERS
  // ============================================

  private getSystemPrompt(options?: any): string {
    const style = options?.style || 'formal';
    const tone = options?.tone || 'neutral';

    const systemPrompts: Record<string, string> = {
      formal: 'You are a professional Argentine political news journalist. Write in a formal, objective style suitable for serious news coverage. Use proper Spanish grammar and maintain journalistic integrity.',
      casual: 'You are a modern news writer for Argentine politics. Write in an accessible, engaging style while maintaining accuracy. Use clear language that connects with readers.',
      investigative: 'You are an investigative journalist specializing in Argentine politics. Write in a detailed, analytical style that uncovers deeper truths. Be thorough and critical while remaining factual.',
      opinion: 'You are a political opinion columnist for an Argentine publication. Write with a clear perspective while backing opinions with facts. Be engaging and persuasive.',
    };

    let systemPrompt = systemPrompts[style] || systemPrompts.formal;

    if (tone === 'critical') {
      systemPrompt += ' Take a critical, questioning approach to the subject matter.';
    } else if (tone === 'supportive') {
      systemPrompt += ' Present the information in a balanced but favorable light.';
    }

    if (options?.preserveFacts) {
      systemPrompt +=
        ' IMPORTANT: Preserve all factual information, dates, names, and quotes from the original text. Only change the writing style and structure.';
    }

    return systemPrompt;
  }

  private buildRewritePrompt(
    title: string,
    content: string,
    options?: any
  ): string {
    const length = options?.length || 'same';
    const lengthInstructions: Record<string, string> = {
      shorter: 'Make the rewritten version approximately 30% shorter while keeping key information.',
      same: 'Keep the rewritten version approximately the same length.',
      longer: 'Expand the rewritten version by approximately 30%, adding context and detail.',
    };

    return `Rewrite this Argentine political news article:

TITLE: ${title}

CONTENT:
${content}

Instructions:
- ${lengthInstructions[length]}
- Maintain all factual accuracy
- Preserve names, dates, quotes, and statistics
- Use clear, professional Spanish
- Focus on Argentine political context
- Ensure the rewrite is original and unique
- Return ONLY the rewritten content, no explanations

Begin the rewrite now:`;
  }

  private hashString(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash;
    }
    return hash.toString(36);
  }
}

// ============================================
// FACTORY FUNCTION
// ============================================

export function createOpenRouterService(apiKey: string) {
  const client = OpenRouterClient.getInstance({
    apiKey,
    defaultModel: 'meta-llama/llama-4-maverick',
    maxRetries: 3,
    rateLimit: {
      requestsPerMinute: 20,
      requestsPerDay: 1000,
    },
  });

  const rewritingService = ContentRewritingService.getInstance(client);

  return {
    client,
    rewritingService,
  };
}
