interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  message?: string;
}

const sizes: Record<string, string> = {
  sm: "h-4 w-4",
  md: "h-8 w-8",
  lg: "h-12 w-12",
};

export const LoadingSpinner = ({
  size = "md",
  message,
}: LoadingSpinnerProps) => {
  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={`${sizes[size]} animate-spin rounded-full border-2 border-primary-400 border-t-ucl-gold`}
      />
      {message && (
        <p className="text-sm text-primary-300 animate-pulse">{message}</p>
      )}
    </div>
  );
};
