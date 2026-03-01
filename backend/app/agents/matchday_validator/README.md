# Matchday Validator Agent

## What This Is
Confirms the matchday extracted from the screenshot or requests manual input.

## Design Decisions
- User-provided matchday always takes priority over AI extraction.
- If matchday is missing from the image, immediately returns a clarification request
  rather than guessing — wrong matchday invalidates the entire analysis.
- Detects when analysis is run too early (>48h before kickoff) and sets `early_warning`.
