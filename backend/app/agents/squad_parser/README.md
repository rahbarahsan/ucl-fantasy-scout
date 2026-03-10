# Squad Parser Agent

## What This Is

Extracts player data (name, position, team, price, substitute status) and matchday
information from a UCL Fantasy squad screenshot using vision-capable AI models.

## How It Works

1. Sends the screenshot with a structured prompt to the AI provider's vision endpoint.
2. Parses the JSON response containing a list of players and optional matchday.
3. Validates basic structure and returns a normalised dict.

## Design Decisions

- Uses vision-only (no OCR library) — AI vision models handle varied screenshot layouts better.
- Returns `matchday: null` when uncertain — the downstream Matchday Validator agent handles clarification.

## Known Limitations

- Very low-resolution or heavily cropped images may produce partial extraction.
- Non-English UCL Fantasy apps may confuse player name / team extraction.
