import type {
  AnalysisResult,
  MatchdayClarification,
  Player,
  Alternative,
} from "../types";

interface RawPlayer {
  name: string;
  position: string;
  team: string;
  status: string;
  reason: string;
  confidence: string;
  price: string;
  is_substitute: boolean;
  alternatives: RawAlternative[];
}

interface RawAlternative {
  name: string;
  team: string;
  position: string;
  price: string;
  reason: string;
}

interface RawAnalysisResponse {
  matchday: string;
  matchday_confirmed: boolean;
  analysis_day: string;
  early_warning: boolean;
  players: RawPlayer[];
}

interface RawClarification {
  needs_clarification: boolean;
  message: string;
}

/**
 * Type-safe parsing of the backend analysis response.
 */
export const parseAnalysisResponse = (
  data: unknown,
): AnalysisResult | MatchdayClarification => {
  const obj = data as Record<string, unknown>;

  // Check if it's a clarification response
  if (obj.needs_clarification) {
    const raw = obj as unknown as RawClarification;
    return {
      needsClarification: true,
      message: raw.message,
    };
  }

  const raw = obj as unknown as RawAnalysisResponse;
  const players: Player[] = raw.players.map((p) => ({
    name: p.name,
    position: p.position as Player["position"],
    team: p.team,
    status: p.status as Player["status"],
    reason: p.reason,
    confidence: p.confidence as Player["confidence"],
    price: p.price,
    isSubstitute: p.is_substitute,
    alternatives: p.alternatives.map(
      (a): Alternative => ({
        name: a.name,
        team: a.team,
        position: a.position,
        price: a.price,
        reason: a.reason,
      }),
    ),
  }));

  return {
    matchday: raw.matchday,
    matchdayConfirmed: raw.matchday_confirmed,
    analysisDay: raw.analysis_day as AnalysisResult["analysisDay"],
    earlyWarning: raw.early_warning,
    players,
  };
};
