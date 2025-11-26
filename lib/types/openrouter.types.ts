/**
 * OPENROUTER TYPE DEFINITIONS
 *
 * Comprehensive type definitions for OpenRouter integration
 */

// ============================================
// OPENROUTER API TYPES
// ============================================

export type OpenRouterModel =
  | 'meta-llama/llama-4-maverick'
  | 'meta-llama/llama-4-scout'
  | 'google/gemini-1.5-pro'
  | 'google/gemini-flash-1.5'
  | 'anthropic/claude-3.5-sonnet'
  | 'openai/gpt-4o'
  | 'openai/gpt-4o-mini'
  | 'zhipu/glm-4.5'
  | 'zhipu/glm-4.5-air'
  | 'inflection/inflection-3-productivity'
  | 'mistralai/mistral-large-2411'
  | string; // Allow custom models

export type MessageRole = 'system' | 'user' | 'assistant';

export type FinishReason =
  | 'stop'
  | 'length'
  | 'tool_calls'
  | 'content_filter'
  | 'error';

// ============================================
// CONTENT REWRITING TYPES
// ============================================

export type WritingStyle =
  | 'formal'
  | 'casual'
  | 'investigative'
  | 'opinion';

export type WritingTone =
  | 'neutral'
  | 'critical'
  | 'supportive';

export type ContentLength =
  | 'shorter'
  | 'same'
  | 'longer';

export type HeadlineStyle =
  | 'clickbait'
  | 'professional'
  | 'investigative';

export type JobStatus =
  | 'pending'
  | 'processing'
  | 'completed'
  | 'failed';

// ============================================
// REQUEST/RESPONSE INTERFACES
// ============================================

export interface RewriteArticleRequest {
  noticiaId: string;
  style?: WritingStyle;
  tone?: WritingTone;
  length?: ContentLength;
  updateOriginal?: boolean;
  generateNewHeadline?: boolean;
  model?: OpenRouterModel;
}

export interface RewriteArticleResponse {
  success: boolean;
  job: RewriteJob;
}

export interface BatchRewriteRequest {
  category?: string;
  limit?: number;
  style?: WritingStyle;
  tone?: WritingTone;
  model?: OpenRouterModel;
}

export interface BatchRewriteResponse {
  success: boolean;
  jobs: RewriteJob[];
  count: number;
}

export interface EnhanceArticleRequest {
  noticiaId: string;
}

export interface EnhanceArticleResponse {
  success: boolean;
  enhancements: {
    improvedTitle: string;
    improvedExcerpt: string;
    suggestions: string[];
  };
}

export interface RewriteStatsResponse {
  success: boolean;
  stats: {
    totalJobs: number;
    completed: number;
    failed: number;
    pending: number;
    processing: number;
    openRouterStats: {
      rateLimit: {
        dailyRequests: number;
        recentRequests: number;
        lastReset: string;
      };
      costs: Record<string, {
        totalCost: number;
        totalTokens: number;
      }>;
      totalCost: number;
    };
  };
}

// ============================================
// JOB TYPES
// ============================================

export interface RewriteJob {
  id: string;
  noticiaId: string;
  status: JobStatus;
  config: RewriteJobConfig;
  result?: RewriteJobResult;
  error?: string;
  createdAt: string;
  completedAt?: string;
}

export interface RewriteJobConfig {
  noticiaId: string;
  style?: WritingStyle;
  tone?: WritingTone;
  length?: ContentLength;
  updateOriginal?: boolean;
  generateNewHeadline?: boolean;
  model?: OpenRouterModel;
}

export interface RewriteJobResult {
  originalTitle: string;
  rewrittenTitle?: string;
  originalContent: string;
  rewrittenContent: string;
  tokensUsed: number;
  cost: number;
  model: string;
}

// ============================================
// API CLIENT TYPES
// ============================================

export interface OpenRouterClientConfig {
  apiKey: string;
  baseUrl?: string;
  defaultModel?: OpenRouterModel;
  maxRetries?: number;
  timeout?: number;
  rateLimit?: {
    requestsPerMinute: number;
    requestsPerDay: number;
  };
}

export interface ChatCompletionMessage {
  role: MessageRole;
  content: string;
}

export interface ChatCompletionRequest {
  model: OpenRouterModel;
  messages: ChatCompletionMessage[];
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  top_k?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stream?: boolean;
  response_format?: { type: 'json_object' };
}

export interface ChatCompletionResponse {
  id: string;
  model: string;
  choices: Array<{
    message: {
      role: string;
      content: string;
    };
    finish_reason: FinishReason;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  created: number;
}

export interface OpenRouterError {
  error: {
    code: number;
    message: string;
    metadata?: Record<string, any>;
  };
}

// ============================================
// COST TRACKING TYPES
// ============================================

export interface ModelPricing {
  input: number;  // Cost per 1M tokens
  output: number; // Cost per 1M tokens
}

export interface CostStats {
  totalCost: number;
  totalTokens: number;
  byModel: Record<string, {
    cost: number;
    tokens: number;
  }>;
}

export interface RateLimitStats {
  dailyRequests: number;
  recentRequests: number;
  lastReset: string;
}

// ============================================
// UTILITY TYPES
// ============================================

export interface GenerateHeadlineOptions {
  style?: HeadlineStyle;
  maxLength?: number;
  includeSubtitle?: boolean;
}

export interface GenerateHeadlineResult {
  headline: string;
  subtitle?: string;
}

export interface SummarizeOptions {
  targetLength?: number;
  style?: WritingStyle;
}

export interface RewriteOptions {
  style?: WritingStyle;
  tone?: WritingTone;
  length?: ContentLength;
  preserveFacts?: boolean;
  model?: OpenRouterModel;
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
// VALIDATION TYPES
// ============================================

export const VALID_STYLES: WritingStyle[] = [
  'formal',
  'casual',
  'investigative',
  'opinion',
];

export const VALID_TONES: WritingTone[] = [
  'neutral',
  'critical',
  'supportive',
];

export const VALID_LENGTHS: ContentLength[] = [
  'shorter',
  'same',
  'longer',
];

export const PREMIUM_MODELS: OpenRouterModel[] = [
  'meta-llama/llama-4-maverick',
  'meta-llama/llama-4-scout',
  'google/gemini-1.5-pro',
  'anthropic/claude-3.5-sonnet',
  'openai/gpt-4o',
];

export const COST_EFFECTIVE_MODELS: OpenRouterModel[] = [
  'zhipu/glm-4.5',
  'zhipu/glm-4.5-air',
  'inflection/inflection-3-productivity',
  'google/gemini-flash-1.5',
  'openai/gpt-4o-mini',
];

export const FREE_MODELS: OpenRouterModel[] = [
  'google/gemini-flash-1.5:free',
  'meta-llama/llama-3.2-3b-instruct:free',
  'mistralai/mistral-7b-instruct:free',
];

// ============================================
// TYPE GUARDS
// ============================================

export function isValidStyle(style: any): style is WritingStyle {
  return VALID_STYLES.includes(style);
}

export function isValidTone(tone: any): tone is WritingTone {
  return VALID_TONES.includes(tone);
}

export function isValidLength(length: any): length is ContentLength {
  return VALID_LENGTHS.includes(length);
}

export function isOpenRouterError(error: any): error is OpenRouterError {
  return error && typeof error.error === 'object' && 'message' in error.error;
}
