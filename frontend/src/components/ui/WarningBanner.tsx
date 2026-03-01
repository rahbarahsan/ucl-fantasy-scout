interface WarningBannerProps {
  message: string;
}

export const WarningBanner = ({ message }: WarningBannerProps) => {
  return (
    <div className="rounded-lg border border-yellow-500/30 bg-yellow-900/20 p-4 text-yellow-300">
      <div className="flex items-start gap-2">
        <span className="text-yellow-400 mt-0.5">⚠</span>
        <p className="text-sm">{message}</p>
      </div>
    </div>
  );
};
