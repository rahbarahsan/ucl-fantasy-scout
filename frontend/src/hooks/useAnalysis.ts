import { useState, useCallback } from "react";
import type {
  ProviderKey,
  AnalysisResult,
  MatchdayClarification,
} from "../types";
import { analyseSquad } from "../services/api";

type AnalysisState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "clarification"; data: MatchdayClarification }
  | { status: "success"; data: AnalysisResult }
  | { status: "error"; message: string };

interface UseAnalysisReturn {
  state: AnalysisState;
  analyse: (
    imageBase64: string,
    provider: ProviderKey,
    matchday?: string,
    apiKey?: string,
  ) => Promise<void>;
  reset: () => void;
}

export const useAnalysis = (): UseAnalysisReturn => {
  const [state, setState] = useState<AnalysisState>({ status: "idle" });

  const analyse = useCallback(
    async (
      imageBase64: string,
      provider: ProviderKey,
      matchday?: string,
      apiKey?: string,
    ) => {
      setState({ status: "loading" });
      try {
        const result = await analyseSquad(imageBase64, provider, matchday, {
          apiKey,
        });

        if ("needsClarification" in result && result.needsClarification) {
          setState({ status: "clarification", data: result });
        } else {
          setState({ status: "success", data: result as AnalysisResult });
        }
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Analysis failed.";
        setState({ status: "error", message });
      }
    },
    [],
  );

  const reset = useCallback(() => {
    setState({ status: "idle" });
  }, []);

  return { state, analyse, reset };
};
