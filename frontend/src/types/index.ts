export type ProviderKey = "anthropic" | "gemini";
export type PlayerStatus = "START" | "RISK" | "BENCH";
export type Position = "GK" | "DEF" | "MID" | "FWD";
export type Confidence = "HIGH" | "MEDIUM" | "LOW";
export type AnalysisDay = "DAY_1" | "DAY_2" | "BOTH";

export interface Alternative {
  name: string;
  team: string;
  position: string;
  price: string;
  reason: string;
}

export interface Player {
  name: string;
  position: Position;
  team: string;
  status: PlayerStatus;
  reason: string;
  confidence: Confidence;
  price: string;
  isSubstitute: boolean;
  alternatives: Alternative[];
}

export interface AnalysisResult {
  matchday: string;
  matchdayConfirmed: boolean;
  analysisDay: AnalysisDay;
  earlyWarning: boolean;
  players: Player[];
}

export interface MatchdayClarification {
  needsClarification: true;
  message: string;
}

export interface ResearchResponse {
  answer: string;
  sources: string[];
}

export interface ProviderConfig {
  provider: ProviderKey;
  apiKey: string;
  isEnvConfigured: boolean;
}

export interface HealthStatus {
  status: string;
  environment: string;
  anthropicConfigured: string;
  geminiConfigured: string;
}
