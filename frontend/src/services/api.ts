import type {
  ProviderKey,
  AnalysisResult,
  MatchdayClarification,
  ResearchResponse,
  HealthStatus,
} from "../types";
import { parseAnalysisResponse } from "../utils/parseResponse";

const BASE_URL = "/api";

interface FetchOptions {
  apiKey?: string;
}

const buildHeaders = (opts?: FetchOptions): Record<string, string> => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (opts?.apiKey) {
    headers["X-API-Key"] = opts.apiKey;
  }
  return headers;
};

/**
 * POST /api/analyse — upload squad screenshot for analysis.
 */
export const analyseSquad = async (
  imageBase64: string,
  provider: ProviderKey,
  matchday?: string,
  opts?: FetchOptions,
): Promise<AnalysisResult | MatchdayClarification> => {
  const resp = await fetch(`${BASE_URL}/analyse`, {
    method: "POST",
    headers: buildHeaders(opts),
    body: JSON.stringify({
      image_base64: imageBase64,
      provider,
      matchday: matchday ?? null,
    }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(
      (err as Record<string, string>).detail ?? `HTTP ${resp.status}`,
    );
  }

  const data: unknown = await resp.json();
  return parseAnalysisResponse(data);
};

/**
 * POST /api/research — ask a free-form question.
 */
export const askResearch = async (
  question: string,
  provider: ProviderKey,
  opts?: FetchOptions,
): Promise<ResearchResponse> => {
  const resp = await fetch(`${BASE_URL}/research`, {
    method: "POST",
    headers: buildHeaders(opts),
    body: JSON.stringify({ question, provider }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(
      (err as Record<string, string>).detail ?? `HTTP ${resp.status}`,
    );
  }

  return (await resp.json()) as ResearchResponse;
};

/**
 * GET /health — check backend status.
 */
export const checkHealth = async (): Promise<HealthStatus> => {
  const resp = await fetch("/health");
  if (!resp.ok) {
    throw new Error("Backend is not reachable.");
  }
  const data = (await resp.json()) as Record<string, string>;
  return {
    status: data.status,
    environment: data.environment,
    anthropicConfigured: data.anthropic_configured,
    geminiConfigured: data.gemini_configured,
  };
};
