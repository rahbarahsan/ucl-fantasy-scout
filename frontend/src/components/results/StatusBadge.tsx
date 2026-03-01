import type { PlayerStatus } from "../../types";

interface StatusBadgeProps {
  status: PlayerStatus;
}

const config: Record<PlayerStatus, { label: string; className: string }> = {
  START: {
    label: "START ✅",
    className: "bg-green-500/20 text-green-400 border-green-500/30",
  },
  RISK: {
    label: "RISK ⚠️",
    className: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  },
  BENCH: {
    label: "BENCH ❌",
    className: "bg-red-500/20 text-red-400 border-red-500/30",
  },
};

export const StatusBadge = ({ status }: StatusBadgeProps) => {
  const { label, className } = config[status];
  return (
    <span
      className={`inline-block rounded-full border px-3 py-1 text-xs font-bold ${className}`}
    >
      {label}
    </span>
  );
};
