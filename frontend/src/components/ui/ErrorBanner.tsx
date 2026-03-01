interface ErrorBannerProps {
  message: string;
  onDismiss?: () => void;
}

export const ErrorBanner = ({ message, onDismiss }: ErrorBannerProps) => {
  return (
    <div className="rounded-lg border border-red-500/30 bg-red-900/20 p-4 text-red-300">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2">
          <span className="text-red-400 mt-0.5">✕</span>
          <p className="text-sm">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-red-400 hover:text-red-300 text-sm"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
};
