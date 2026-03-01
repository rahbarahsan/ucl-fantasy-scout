import { useState, useCallback } from "react";
import type { ProviderKey, ResearchResponse } from "../types";
import { askResearch } from "../services/api";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
}

interface UseAdHocResearchReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  ask: (
    question: string,
    provider: ProviderKey,
    apiKey?: string,
  ) => Promise<void>;
  clear: () => void;
}

export const useAdHocResearch = (): UseAdHocResearchReturn => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = useCallback(
    async (question: string, provider: ProviderKey, apiKey?: string) => {
      setError(null);
      setMessages((prev) => [...prev, { role: "user", content: question }]);
      setIsLoading(true);

      try {
        const response: ResearchResponse = await askResearch(
          question,
          provider,
          { apiKey },
        );
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: response.answer,
            sources: response.sources,
          },
        ]);
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : "Research request failed.";
        setError(message);
      } finally {
        setIsLoading(false);
      }
    },
    [],
  );

  const clear = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, isLoading, error, ask, clear };
};
