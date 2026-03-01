# Verdict Engine Agent

## What This Is
Synthesises all upstream research (previews, form, stats) into a final
START / RISK / BENCH verdict for each player.

## Design Decisions
- Uses `rules.py` heuristics as a reference, but the actual synthesis is
  done by the AI model which can weigh conflicting signals in context.
- Communicates uncertainty clearly — confidence is HIGH / MEDIUM / LOW.
- Includes 2-3 sentence reasoning per player so users understand the verdict.
