import { useCallback, useEffect, useRef } from "react";
import { Button } from "../ui/Button";

interface SquadUploaderProps {
  onFile: (file: File) => Promise<void>;
  onPaste: (event: ClipboardEvent) => Promise<void>;
  onDrop: (event: React.DragEvent) => Promise<void>;
  imagePreview: string | null;
  fileName: string | null;
  isLoading: boolean;
  error: string | null;
  onClear: () => void;
}

export const SquadUploader = ({
  onFile,
  onPaste,
  onDrop,
  imagePreview,
  fileName,
  isLoading,
  error,
  onClear,
}: SquadUploaderProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handler = (e: ClipboardEvent) => {
      onPaste(e);
    };
    document.addEventListener("paste", handler);
    return () => document.removeEventListener("paste", handler);
  }, [onPaste]);

  const handleFileChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) await onFile(file);
    },
    [onFile],
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  if (imagePreview) {
    return (
      <div className="flex flex-col items-center gap-4 rounded-xl border border-primary-600 bg-primary-800/50 p-6">
        <img
          src={imagePreview}
          alt="Squad screenshot"
          className="max-h-64 rounded-lg object-contain"
        />
        <p className="text-sm text-primary-300">{fileName}</p>
        <Button variant="secondary" onClick={onClear}>
          Remove & Upload New
        </Button>
      </div>
    );
  }

  return (
    <div
      onDrop={onDrop}
      onDragOver={handleDragOver}
      className="flex flex-col items-center gap-4 rounded-xl border-2 border-dashed border-primary-600 bg-primary-800/30 p-10 transition-colors hover:border-ucl-gold/50"
    >
      <div className="text-center">
        <p className="text-4xl mb-3">📸</p>
        <p className="text-lg font-medium text-white">
          Upload your squad screenshot
        </p>
        <p className="mt-1 text-sm text-primary-400">
          Drag & drop, paste from clipboard, or click to select
        </p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={handleFileChange}
        className="hidden"
      />

      <Button
        onClick={() => fileInputRef.current?.click()}
        disabled={isLoading}
      >
        {isLoading ? "Processing…" : "Choose File"}
      </Button>

      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
};
