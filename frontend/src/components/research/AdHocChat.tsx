import { useState, useRef, useCallback } from "react";
import type { ProviderKey } from "../../types";
import { Button } from "../ui/Button";
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { ErrorBanner } from "../ui/ErrorBanner";
import { useAdHocResearch } from "../../hooks/useAdHocResearch";

interface AdHocChatProps {
  provider: ProviderKey;
  apiKey?: string;
}

export const AdHocChat = ({ provider, apiKey }: AdHocChatProps) => {
  const [input, setInput] = useState("");
  const { messages, isLoading, error, ask, clear } = useAdHocResearch();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!input.trim() || isLoading) return;
      const question = input.trim();
      setInput("");
      await ask(question, provider, apiKey);
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    },
    [input, isLoading, ask, provider, apiKey],
  );

  return (
    <div className="flex flex-col gap-4 rounded-xl border border-primary-600 bg-primary-800/50 p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-white">Research Chat</h3>
        {messages.length > 0 && (
          <Button variant="secondary" onClick={clear}>
            Clear
          </Button>
        )}
      </div>

      {/* Messages */}
      <div className="flex max-h-96 flex-col gap-3 overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-sm text-primary-400">
            Ask anything about UCL Fantasy — e.g. &quot;Is Vinicius Jr likely to
            start?&quot;
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`rounded-lg p-3 text-sm ${
              msg.role === "user"
                ? "ml-8 bg-ucl-gold/10 text-ucl-gold"
                : "mr-8 bg-primary-700 text-primary-200"
            }`}
          >
            <p className="whitespace-pre-wrap">{msg.content}</p>
            {msg.sources && msg.sources.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {msg.sources.map((src, j) => (
                  <a
                    key={j}
                    href={src}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-ucl-gold/60 underline hover:text-ucl-gold"
                  >
                    Source {j + 1}
                  </a>
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && <LoadingSpinner size="sm" message="Researching…" />}
        <div ref={messagesEndRef} />
      </div>

      {error && <ErrorBanner message={error} />}

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a UCL Fantasy research question…"
          className="flex-1 rounded-lg bg-primary-700 px-3 py-2 text-sm text-white placeholder-primary-400 focus:outline-none focus:ring-2 focus:ring-ucl-gold"
          disabled={isLoading}
        />
        <Button type="submit" disabled={isLoading || !input.trim()}>
          Ask
        </Button>
      </form>
    </div>
  );
};
