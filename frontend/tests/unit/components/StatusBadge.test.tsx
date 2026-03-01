import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusBadge } from "../../../src/components/results/StatusBadge";

describe("StatusBadge", () => {
  it("renders START badge", () => {
    render(<StatusBadge status="START" />);
    expect(screen.getByText(/START/)).toBeDefined();
  });

  it("renders RISK badge", () => {
    render(<StatusBadge status="RISK" />);
    expect(screen.getByText(/RISK/)).toBeDefined();
  });

  it("renders BENCH badge", () => {
    render(<StatusBadge status="BENCH" />);
    expect(screen.getByText(/BENCH/)).toBeDefined();
  });
});
