import type { Player, PlayerStatus } from "../../types";
import { PlayerCard } from "./PlayerCard";

interface PlayerGroupProps {
  status: PlayerStatus;
  players: Player[];
}

const headings: Record<PlayerStatus, string> = {
  START: "Likely Starters",
  RISK: "At Risk",
  BENCH: "Likely Benched",
};

export const PlayerGroup = ({ status, players }: PlayerGroupProps) => {
  if (players.length === 0) return null;

  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-lg font-bold text-white">
        {headings[status]}{" "}
        <span className="text-sm font-normal text-primary-400">
          ({players.length})
        </span>
      </h2>
      <div className="flex flex-col gap-3">
        {players.map((player) => (
          <PlayerCard key={player.name} player={player} />
        ))}
      </div>
    </div>
  );
};
