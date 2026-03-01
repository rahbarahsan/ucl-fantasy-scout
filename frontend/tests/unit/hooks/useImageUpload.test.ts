import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useImageUpload } from "../../../src/hooks/useImageUpload";

// Mock FileReader
const mockReadAsDataURL = vi.fn();
class MockFileReader {
  result: string | null = null;
  onload: (() => void) | null = null;
  onerror: (() => void) | null = null;
  readAsDataURL = mockReadAsDataURL;
}

vi.stubGlobal("FileReader", MockFileReader);

describe("useImageUpload", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("starts with empty state", () => {
    const { result } = renderHook(() => useImageUpload());
    expect(result.current.imageData).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.preview).toBeNull();
  });

  it("rejects non-image files", () => {
    const { result } = renderHook(() => useImageUpload());
    const file = new File(["hello"], "test.txt", { type: "text/plain" });

    act(() => {
      result.current.handleFile(file);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.imageData).toBeNull();
  });

  it("clears state on reset", () => {
    const { result } = renderHook(() => useImageUpload());

    act(() => {
      result.current.reset();
    });

    expect(result.current.imageData).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.preview).toBeNull();
  });
});
