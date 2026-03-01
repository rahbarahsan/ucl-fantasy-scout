import { useState } from "react";
import type { ProviderKey } from "../../types";

interface ApiKeyInputProps {
  provider: ProviderKey;
  value: string;
  onChange: (key: string) => void;
  isEnvConfigured: boolean;
}

export const ApiKeyInput = ({
  provider,
  value,
  onChange,
  isEnvConfigured,
}: ApiKeyInputProps) => {
  const [isVisible, setIsVisible] = useState(false);

  if (isEnvConfigured) {
    return (
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-primary-300">
          {provider === "anthropic" ? "Anthropic" : "Gemini"} API Key
        </label>
        <div className="flex items-center gap-2 rounded-lg bg-primary-700/50 px-3 py-2">
          <span className="text-green-400 text-sm">✓</span>
          <span className="text-sm text-primary-300">
            Configured via environment
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm font-medium text-primary-300">
        {provider === "anthropic" ? "Anthropic" : "Gemini"} API Key
      </label>
      <div className="flex gap-2">
        <input
          type={isVisible ? "text" : "password"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={`Enter your ${provider} API key…`}
          className="flex-1 rounded-lg bg-primary-700 px-3 py-2 text-sm text-white placeholder-primary-400 focus:outline-none focus:ring-2 focus:ring-ucl-gold"
        />
        <button
          onClick={() => setIsVisible(!isVisible)}
          className="rounded-lg bg-primary-700 px-3 py-2 text-sm text-primary-300 hover:bg-primary-600"
        >
          {isVisible ? "Hide" : "Show"}
        </button>
      </div>
      <p className="text-xs text-primary-400">
        Key is encrypted in your browser session and never stored.
      </p>
    </div>
  );
};
