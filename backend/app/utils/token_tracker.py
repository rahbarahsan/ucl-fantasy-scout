"""Token usage tracker for the entire pipeline."""

from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Provider pricing (as of 2026-02-28)
PRICING = {
    "anthropic": {
        "input": 3.00,      # $3 per 1M input tokens
        "output": 15.00,    # $15 per 1M output tokens
    },
    "gemini": {
        "input": 0.075,     # $0.075 per 1M input tokens
        "output": 0.30,     # $0.30 per 1M output tokens
    }
}


class TokenUsageTracker:
    """Track token usage and cost per analysis."""

    def __init__(self, provider_name: str = "anthropic"):
        """Initialize tracker for a specific provider."""
        self.provider_name = provider_name
        self.input_tokens = 0
        self.output_tokens = 0
        self.agents_called: list[str] = []

    def add_input(self, count: int, agent_name: str = "") -> None:
        """Record input tokens."""
        self.input_tokens += count
        if agent_name:
            self.agents_called.append(agent_name)
            logger.debug(
                "tokens_input",
                agent=agent_name,
                count=count,
                total=self.input_tokens
            )

    def add_output(self, count: int, agent_name: str = "") -> None:
        """Record output tokens."""
        self.output_tokens += count
        if agent_name:
            logger.debug(
                "tokens_output",
                agent=agent_name,
                count=count,
                total=self.output_tokens
            )

    def total_tokens(self) -> int:
        """Return total tokens used."""
        return self.input_tokens + self.output_tokens

    def cost_usd(self) -> float:
        """Calculate cost in USD."""
        pricing = PRICING.get(self.provider_name, PRICING["anthropic"])
        
        input_cost = (self.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (self.output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost

    def print_summary(self) -> None:
        """Print token usage and cost summary."""
        print("\n" + "=" * 70)
        print(f"TOKEN USAGE & COST SUMMARY ({self.provider_name.upper()})")
        print("=" * 70)
        print(f"  Input Tokens: {self.input_tokens:,}")
        print(f"  Output Tokens: {self.output_tokens:,}")
        print(f"  Total Tokens: {self.total_tokens():,}")
        print(f"  Cost: ${self.cost_usd():.4f}")
        print(f"  Agents Called: {len(set(self.agents_called))}")
        print("=" * 70 + "\n")

    def to_dict(self) -> dict:
        """Return usage as dictionary."""
        return {
            "provider": self.provider_name,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens(),
            "cost_usd": self.cost_usd(),
            "agents_called": len(set(self.agents_called))
        }


# Global tracker (reset per analysis)
current_tracker: Optional[TokenUsageTracker] = None


def reset_tracker(provider_name: str = "anthropic") -> TokenUsageTracker:
    """Reset the global tracker for a new analysis."""
    global current_tracker
    current_tracker = TokenUsageTracker(provider_name)
    logger.info("tracker_reset", provider=provider_name)
    return current_tracker


def get_tracker() -> Optional[TokenUsageTracker]:
    """Get the current tracker."""
    return current_tracker
