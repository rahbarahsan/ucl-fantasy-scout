import type { AnalysisResult, PlayerStatus } from "../../types";
import { WarningBanner } from "../ui/WarningBanner";
import { PlayerGroup } from "./PlayerGroup";

interface ResultsSummaryProps {
  result: AnalysisResult;
}

const statusOrder: PlayerStatus[] = ["START", "RISK", "BENCH"];

export const ResultsSummary = ({ result }: ResultsSummaryProps) => {
  const counts: Record<PlayerStatus, number> = {
    START: result.players.filter((p) => p.status === "START").length,
    RISK: result.players.filter((p) => p.status === "RISK").length,
    BENCH: result.players.filter((p) => p.status === "BENCH").length,
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">
          {result.matchday} — Squad Report
        </h2>
        <span className="text-sm text-primary-400">
          {result.analysisDay === "BOTH" ? "All fixtures" : result.analysisDay}
        </span>
      </div>

      {/* Early warning */}
      {result.earlyWarning && (
        <WarningBanner message="Analysis was run early — predictions may change as kickoff approaches. Re-run closer to the deadline for better accuracy." />
      )}

      {/* Count badges */}
      <div className="flex gap-3">
        <span className="rounded-lg bg-green-500/20 px-4 py-2 text-sm font-bold text-green-400">
          {counts.START} Starting
        </span>
        <span className="rounded-lg bg-yellow-500/20 px-4 py-2 text-sm font-bold text-yellow-400">
          {counts.RISK} At Risk
        </span>
        <span className="rounded-lg bg-red-500/20 px-4 py-2 text-sm font-bold text-red-400">
          {counts.BENCH} Benched
        </span>
      </div>

      {/* Player groups */}
      {statusOrder.map((status) => (
        <PlayerGroup
          key={status}
          status={status}
          players={result.players.filter((p) => p.status === status)}
        />
      ))}
    </div>
  );
};
