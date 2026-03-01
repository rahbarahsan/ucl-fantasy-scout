"""Heuristic rules for the Verdict Engine."""

# Minutes thresholds
FULL_MATCH_MINUTES = 85  # Considered a full 90
LOW_MINUTES_THRESHOLD = 30  # Likely being rested / managed

# Rotation risk multipliers
ROTATION_RISK_WEIGHTS = {
    "HIGH": 0.3,  # strong chance of being benched
    "MEDIUM": 0.15,
    "LOW": 0.0,
}

# Form modifiers
FORM_MODIFIERS = {
    "GOOD": 0.1,  # positive boost to start probability
    "AVERAGE": 0.0,
    "POOR": -0.1,
}

# Expected lineup presence modifier
IN_PREDICTED_LINEUP = 0.3
NOT_IN_PREDICTED_LINEUP = -0.2

# Thresholds for final verdict
START_THRESHOLD = 0.55
BENCH_THRESHOLD = 0.30
# Between BENCH_THRESHOLD and START_THRESHOLD → RISK

# Confidence mapping
HIGH_CONFIDENCE_DELTA = 0.25  # if score is far from thresholds
LOW_CONFIDENCE_DELTA = 0.10  # if score is close to a threshold
