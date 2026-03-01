import { useState, useCallback } from "react";
import type { ProviderKey } from "./types";
import { DEFAULT_PROVIDER } from "./constants/providers";
import { Header } from "./components/layout/Header";
import { ProviderSelector } from "./components/settings/ProviderSelector";
import { ApiKeyInput } from "./components/settings/ApiKeyInput";
import { SquadUploader } from "./components/upload/SquadUploader";
import { MatchdayConfirm } from "./components/matchday/MatchdayConfirm";
import { ResultsSummary } from "./components/results/ResultsSummary";
import { AdHocChat } from "./components/research/AdHocChat";
import { LoadingSpinner } from "./components/ui/LoadingSpinner";
import { ErrorBanner } from "./components/ui/ErrorBanner";
import { useImageUpload } from "./hooks/useImageUpload";
import { useAnalysis } from "./hooks/useAnalysis";

export const App = () => {
  const [provider, setProvider] = useState<ProviderKey>(DEFAULT_PROVIDER);
  const [apiKey, setApiKey] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [activeTab, setActiveTab] = useState<"analyse" | "research">("analyse");

  const imageUpload = useImageUpload();
  const analysis = useAnalysis();

  const handleAnalyse = useCallback(() => {
    if (!imageUpload.imageBase64) return;
    analysis.analyse(
      imageUpload.imageBase64,
      provider,
      undefined,
      apiKey || undefined,
    );
  }, [imageUpload.imageBase64, analysis, provider, apiKey]);

  const handleMatchdayConfirm = useCallback(
    (matchday: string) => {
      if (!imageUpload.imageBase64) return;
      analysis.analyse(
        imageUpload.imageBase64,
        provider,
        matchday,
        apiKey || undefined,
      );
    },
    [imageUpload.imageBase64, analysis, provider, apiKey],
  );

  const handleReset = useCallback(() => {
    analysis.reset();
    imageUpload.clear();
  }, [analysis, imageUpload]);

  return (
    <div className="min-h-screen bg-ucl-dark">
      <Header />

      <main className="mx-auto max-w-3xl px-4 py-8">
        <div className="flex flex-col gap-6">
          {/* Tab switcher */}
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab("analyse")}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === "analyse"
                  ? "bg-ucl-gold text-ucl-dark"
                  : "bg-primary-700 text-primary-300 hover:bg-primary-600"
              }`}
            >
              Squad Analysis
            </button>
            <button
              onClick={() => setActiveTab("research")}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === "research"
                  ? "bg-ucl-gold text-ucl-dark"
                  : "bg-primary-700 text-primary-300 hover:bg-primary-600"
              }`}
            >
              Research Chat
            </button>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="ml-auto rounded-lg bg-primary-700 px-4 py-2 text-sm text-primary-300 hover:bg-primary-600"
            >
              ⚙ Settings
            </button>
          </div>

          {/* Settings panel */}
          {showSettings && (
            <div className="flex flex-col gap-4 rounded-xl border border-primary-600 bg-primary-800/50 p-4">
              <ProviderSelector value={provider} onChange={setProvider} />
              <ApiKeyInput
                provider={provider}
                value={apiKey}
                onChange={setApiKey}
                isEnvConfigured={false}
              />
            </div>
          )}

          {/* Analysis tab */}
          {activeTab === "analyse" && (
            <>
              {/* Upload */}
              {analysis.state.status === "idle" && (
                <>
                  <SquadUploader
                    onFile={imageUpload.handleFile}
                    onPaste={imageUpload.handlePaste}
                    onDrop={imageUpload.handleDrop}
                    imagePreview={imageUpload.imageBase64}
                    fileName={imageUpload.fileName}
                    isLoading={imageUpload.isLoading}
                    error={imageUpload.error}
                    onClear={imageUpload.clear}
                  />
                  {imageUpload.imageBase64 && (
                    <button
                      onClick={handleAnalyse}
                      className="rounded-lg bg-ucl-gold px-6 py-3 text-lg font-bold text-ucl-dark transition-colors hover:bg-yellow-500"
                    >
                      Analyse Squad
                    </button>
                  )}
                </>
              )}

              {/* Loading */}
              {analysis.state.status === "loading" && (
                <div className="py-16">
                  <LoadingSpinner
                    size="lg"
                    message="Analysing your squad — this may take a minute…"
                  />
                </div>
              )}

              {/* Matchday clarification */}
              {analysis.state.status === "clarification" && (
                <MatchdayConfirm
                  message={analysis.state.data.message}
                  onConfirm={handleMatchdayConfirm}
                  onCancel={handleReset}
                />
              )}

              {/* Results */}
              {analysis.state.status === "success" && (
                <div className="flex flex-col gap-6">
                  <ResultsSummary result={analysis.state.data} />
                  <button
                    onClick={handleReset}
                    className="rounded-lg bg-primary-700 px-4 py-2 text-sm text-primary-300 hover:bg-primary-600"
                  >
                    ← Analyse Another Squad
                  </button>
                </div>
              )}

              {/* Error */}
              {analysis.state.status === "error" && (
                <div className="flex flex-col gap-4">
                  <ErrorBanner
                    message={analysis.state.message}
                    onDismiss={handleReset}
                  />
                  <button
                    onClick={handleReset}
                    className="rounded-lg bg-primary-700 px-4 py-2 text-sm text-primary-300 hover:bg-primary-600"
                  >
                    Try Again
                  </button>
                </div>
              )}
            </>
          )}

          {/* Research tab */}
          {activeTab === "research" && (
            <AdHocChat provider={provider} apiKey={apiKey || undefined} />
          )}
        </div>
      </main>
    </div>
  );
};
