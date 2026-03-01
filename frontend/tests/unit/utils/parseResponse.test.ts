import { describe, it, expect } from "vitest";
import { parseAnalysisResponse } from "../../../src/utils/parseResponse";

describe("parseAnalysisResponse", () => {
  it("parses a clarification response", () => {
    const raw = {
      needs_clarification: true,
      message: "Please specify the matchday.",
    };
    const result = parseAnalysisResponse(raw);
    expect("needsClarification" in result).toBe(true);
    if ("needsClarification" in result) {
      expect(result.message).toBe("Please specify the matchday.");
    }
  });

  it("parses a full analysis response", () => {
    const raw = {
      matchday: "Matchday 5",
      matchday_confirmed: true,
      analysis_day: "BOTH",
      early_warning: false,
      players: [
        {
          name: "Haaland",
          position: "FWD",
          team: "Man City",
          status: "START",
          reason: "Nailed starter.",
          confidence: "HIGH",
          price: "11.5",
          is_substitute: false,
          alternatives: [],
        },
      ],
    };
    const result = parseAnalysisResponse(raw);
    expect("players" in result).toBe(true);
    if ("players" in result) {
      expect(result.matchday).toBe("Matchday 5");
      expect(result.players).toHaveLength(1);
      expect(result.players[0].isSubstitute).toBe(false);
    }
  });
});
