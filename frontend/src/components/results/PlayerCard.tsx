import type { Player } from "../../types";
import { StatusBadge } from "./StatusBadge";
import { AlternativeCard } from "./AlternativeCard";

interface PlayerCardProps {
  player: Player;
}

export const PlayerCard = ({ player }: PlayerCardProps) => {
  return (
    <div className="rounded-xl border border-primary-600 bg-primary-800/50 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-white">{player.name}</h3>
            {player.isSubstitute && (
              <span className="rounded bg-primary-600 px-2 py-0.5 text-xs text-primary-300">
                SUB
              </span>
            )}
          </div>
          <p className="text-sm text-primary-400">
            {player.team} · {player.position} · €{player.price}
          </p>
        </div>
        <StatusBadge status={player.status} />
      </div>

      <p className="mt-3 text-sm text-primary-300">{player.reason}</p>

      <div className="mt-2 flex items-center gap-2">
        <span className="text-xs text-primary-400">Confidence:</span>
        <span
          className={`text-xs font-medium ${
            player.confidence === "HIGH"
              ? "text-green-400"
              : player.confidence === "MEDIUM"
                ? "text-yellow-400"
                : "text-red-400"
          }`}
        >
          {player.confidence}
        </span>
      </div>

      {player.alternatives.length > 0 && (
        <div className="mt-4">
          <p className="mb-2 text-xs font-medium text-primary-400">
            Suggested alternatives:
          </p>
          <div className="flex flex-col gap-2">
            {player.alternatives.map((alt) => (
              <AlternativeCard key={alt.name} alternative={alt} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
