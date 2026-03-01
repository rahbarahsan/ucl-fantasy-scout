import { PROVIDERS, DEFAULT_PROVIDER } from "../../constants/providers";
import type { ProviderKey } from "../../types";

interface ProviderSelectorProps {
  value: ProviderKey;
  onChange: (provider: ProviderKey) => void;
}

export const ProviderSelector = ({
  value,
  onChange,
}: ProviderSelectorProps) => {
  const providerKeys = Object.keys(PROVIDERS) as ProviderKey[];

  return (
    <div className="flex flex-col gap-2">
      <label className="text-sm font-medium text-primary-300">
        AI Provider
      </label>
      <div className="flex gap-2">
        {providerKeys.map((key) => (
          <button
            key={key}
            onClick={() => onChange(key)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              value === key
                ? "bg-ucl-gold text-ucl-dark"
                : "bg-primary-700 text-primary-300 hover:bg-primary-600"
            }`}
          >
            {PROVIDERS[key].label}
          </button>
        ))}
      </div>
    </div>
  );
};

ProviderSelector.defaultProps = {
  value: DEFAULT_PROVIDER,
};
