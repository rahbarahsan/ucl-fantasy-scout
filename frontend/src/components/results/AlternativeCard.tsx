import type { Alternative } from "../../types";

interface AlternativeCardProps {
  alternative: Alternative;
}

export const AlternativeCard = ({ alternative }: AlternativeCardProps) => {
  return (
    <div className="rounded-lg border border-primary-600 bg-primary-700/50 p-3">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-white">{alternative.name}</p>
          <p className="text-xs text-primary-400">
            {alternative.team} · {alternative.position} · €{alternative.price}
          </p>
        </div>
        <span className="text-xs text-ucl-gold">→ Transfer In</span>
      </div>
      <p className="mt-2 text-xs text-primary-300">{alternative.reason}</p>
    </div>
  );
};
