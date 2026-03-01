import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PlayerCard } from "../../../src/components/results/PlayerCard";
import type { Player } from "../../../src/types";

const mockPlayer: Player = {
  name: "Haaland",
  position: "FWD",
  team: "Man City",
  status: "START",
  reason: "Nailed starter with excellent form.",
  confidence: "HIGH",
  price: "11.5",
  isSubstitute: false,
  alternatives: [],
};

describe("PlayerCard", () => {
  it("renders player name and team", () => {
    render(<PlayerCard player={mockPlayer} />);
    expect(screen.getByText("Haaland")).toBeDefined();
    expect(screen.getByText(/Man City/)).toBeDefined();
  });

  it("shows SUB label for substitutes", () => {
    render(<PlayerCard player={{ ...mockPlayer, isSubstitute: true }} />);
    expect(screen.getByText("SUB")).toBeDefined();
  });

  it("displays alternatives when present", () => {
    const withAlts: Player = {
      ...mockPlayer,
      status: "BENCH",
      alternatives: [
        {
          name: "Mbappé",
          team: "Real Madrid",
          position: "FWD",
          price: "12.0",
          reason: "Top scorer",
        },
      ],
    };
    render(<PlayerCard player={withAlts} />);
    expect(screen.getByText("Mbappé")).toBeDefined();
  });
});
