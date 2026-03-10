"""Smart matchday normalization for various user input formats."""

import re
from typing import Optional


def normalize_matchday(raw_matchday: Optional[str]) -> str:
    """Normalize various matchday formats to standard UCL terminology.

    Handles:
    - Abbreviations: R16, QF, SF, F
    - Various spellings: "round of 16", "round 16", "last 16"
    - Leg specifications: "1st leg", "first leg", "leg 1"
    - Case variations and extra whitespace

    Returns standard format: "Round of 16 - 1st leg", "Quarter-finals", etc.
    """
    if not raw_matchday:
        return ""

    # Convert to lowercase and clean whitespace
    normalized = raw_matchday.lower().strip()
    normalized = re.sub(r"\s+", " ", normalized)  # Collapse multiple spaces

    # Remove common filler words
    normalized = normalized.replace("the ", "")
    normalized = normalized.replace("knockout ", "")
    normalized = normalized.replace("stage ", "")

    # Detect leg specifications first
    leg = None
    if re.search(r"1st|first|leg\s*1", normalized):
        leg = "1st leg"
    elif re.search(r"2nd|second|leg\s*2", normalized):
        leg = "2nd leg"

    # Remove leg info from main string for cleaner matching
    normalized = re.sub(r"[-–—]\s*(1st|2nd|first|second)\s*leg", "", normalized)
    normalized = re.sub(r"leg\s*[12]", "", normalized)
    normalized = re.sub(r"(1st|2nd|first|second)\s*leg", "", normalized)
    normalized = normalized.strip()

    # Map to standard formats
    stage = _normalize_stage(normalized)

    # Combine stage with leg if present
    if leg and stage:
        return f"{stage} - {leg}"
    return stage or raw_matchday  # Fallback to original if no match


# pylint: disable=too-many-return-statements
def _normalize_stage(stage: str) -> str:
    """Map stage abbreviations and variations to standard names."""
    # Round of 16
    if any(
        x in stage
        for x in [
            "r16",
            "ro16",
            "round of 16",
            "round 16",
            "last 16",
            "16",
            "roundof16",
        ]
    ):
        return "Round of 16"

    # Quarter-finals
    if any(
        x in stage
        for x in [
            "qf",
            "quarter",
            "quarters",
            "quarter-final",
            "quarter final",
            "last 8",
        ]
    ):
        return "Quarter-finals"

    # Semi-finals
    if any(
        x in stage
        for x in ["sf", "semi", "semis", "semi-final", "semi final", "last 4"]
    ):
        return "Semi-finals"

    # Final
    if any(x in stage for x in ["final", "f", "championship"]):
        return "Final"

    # Group stage with variations
    if "group" in stage:
        # Extract group letter if present (e.g., "group a", "md1")
        match = re.search(r"group\s*([a-h])", stage)
        if match:
            return f"Group Stage - Group {match.group(1).upper()}"

        # Extract matchday number if present
        match = re.search(r"(?:matchday|md|day)\s*(\d+)", stage)
        if match:
            return f"Group Stage - Matchday {match.group(1)}"

        return "Group Stage"

    return stage.title()  # Return title-cased version as fallback


def get_search_friendly_matchday(normalized: str) -> str:
    """Convert normalized matchday to search-engine friendly format.

    Examples:
    - "Round of 16 - 1st leg" → "Round of 16 first leg"
    - "Quarter-finals - 2nd leg" → "Quarter finals second leg"
    """
    # Replace hyphens with spaces
    search_friendly = normalized.replace("-", " ")

    # Replace ordinal indicators with words for better search
    search_friendly = search_friendly.replace("1st", "first")
    search_friendly = search_friendly.replace("2nd", "second")

    # Clean up extra spaces
    search_friendly = re.sub(r"\s+", " ", search_friendly).strip()

    return search_friendly
