import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useImageUpload } from "../../../src/hooks/useImageUpload";

describe("useImageUpload", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("starts with empty state", () => {
    const { result } = renderHook(() => useImageUpload());
    expect(result.current.imageBase64).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.fileName).toBeNull();
    expect(result.current.isLoading).toBe(false);
  });

  it("rejects non-image files", () => {
    const { result } = renderHook(() => useImageUpload());
    const file = new File(["hello"], "test.txt", { type: "text/plain" });

    act(() => {
      result.current.handleFile(file);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.imageBase64).toBeNull();
  });

  it("clears state on clear()", () => {
    const { result } = renderHook(() => useImageUpload());

    act(() => {
      result.current.clear();
    });

    expect(result.current.imageBase64).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.fileName).toBeNull();
  });
});
