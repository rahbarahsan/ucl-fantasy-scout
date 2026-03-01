import { useState } from "react";
import { Button } from "../ui/Button";

interface MatchdayConfirmProps {
  message: string;
  onConfirm: (matchday: string) => void;
  onCancel: () => void;
}

export const MatchdayConfirm = ({
  message,
  onConfirm,
  onCancel,
}: MatchdayConfirmProps) => {
  const [matchday, setMatchday] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (matchday.trim()) {
      onConfirm(matchday.trim());
    }
  };

  return (
    <div className="rounded-xl border border-yellow-500/30 bg-yellow-900/10 p-6">
      <div className="flex flex-col gap-4">
        <div className="flex items-start gap-3">
          <span className="text-2xl">📅</span>
          <div>
            <h3 className="font-medium text-yellow-300">
              Matchday Confirmation Needed
            </h3>
            <p className="mt-1 text-sm text-primary-300">{message}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={matchday}
            onChange={(e) => setMatchday(e.target.value)}
            placeholder="e.g. Matchday 5"
            className="flex-1 rounded-lg bg-primary-700 px-3 py-2 text-sm text-white placeholder-primary-400 focus:outline-none focus:ring-2 focus:ring-ucl-gold"
          />
          <Button type="submit" disabled={!matchday.trim()}>
            Confirm
          </Button>
          <Button variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        </form>
      </div>
    </div>
  );
};
