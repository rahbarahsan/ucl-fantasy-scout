import { useState, useCallback, useRef } from "react";
import { imageToBase64 } from "../utils/imageToBase64";

interface UseImageUploadReturn {
  imageBase64: string | null;
  fileName: string | null;
  error: string | null;
  isLoading: boolean;
  handleFile: (file: File) => Promise<void>;
  handlePaste: (event: ClipboardEvent) => Promise<void>;
  handleDrop: (event: React.DragEvent) => Promise<void>;
  clear: () => void;
  inputRef: React.RefObject<HTMLInputElement | null>;
}

const ALLOWED_TYPES = ["image/png", "image/jpeg", "image/webp", "image/gif"];
const MAX_SIZE = 20 * 1024 * 1024; // 20 MB

export const useImageUpload = (): UseImageUploadReturn => {
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const processFile = useCallback(async (file: File) => {
    setError(null);
    if (!ALLOWED_TYPES.includes(file.type)) {
      setError("Unsupported file type. Please upload PNG, JPEG, or WebP.");
      return;
    }
    if (file.size > MAX_SIZE) {
      setError("File is too large. Maximum size is 20 MB.");
      return;
    }
    setIsLoading(true);
    try {
      const base64 = await imageToBase64(file);
      setImageBase64(base64);
      setFileName(file.name);
    } catch {
      setError("Failed to read the image file.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleFile = useCallback(
    async (file: File) => {
      await processFile(file);
    },
    [processFile],
  );

  const handlePaste = useCallback(
    async (event: ClipboardEvent) => {
      const items = event.clipboardData?.items;
      if (!items) return;
      for (const item of items) {
        if (item.type.startsWith("image/")) {
          const file = item.getAsFile();
          if (file) {
            await processFile(file);
            return;
          }
        }
      }
    },
    [processFile],
  );

  const handleDrop = useCallback(
    async (event: React.DragEvent) => {
      event.preventDefault();
      const file = event.dataTransfer.files[0];
      if (file) {
        await processFile(file);
      }
    },
    [processFile],
  );

  const clear = useCallback(() => {
    setImageBase64(null);
    setFileName(null);
    setError(null);
  }, []);

  return {
    imageBase64,
    fileName,
    error,
    isLoading,
    handleFile,
    handlePaste,
    handleDrop,
    clear,
    inputRef,
  };
};
