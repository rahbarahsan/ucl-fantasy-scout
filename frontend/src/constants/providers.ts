import type { ProviderKey } from "../types";

interface ProviderInfo {
  label: string;
  models: string[];
  defaultModel: string;
}

export const PROVIDERS: Record<ProviderKey, ProviderInfo> = {
  anthropic: {
    label: "Anthropic Claude",
    models: ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022"],
    defaultModel: "claude-sonnet-4-20250514",
  },
  gemini: {
    label: "Google Gemini",
    models: ["gemini-2.0-flash", "gemini-2.0-flash-lite"],
    defaultModel: "gemini-2.0-flash",
  },
};

export const DEFAULT_PROVIDER: ProviderKey = "anthropic";
