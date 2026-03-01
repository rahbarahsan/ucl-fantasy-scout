# Fixture Resolver Agent

## What This Is
Maps each player's club to their UCL fixture for the given matchday.

## Design Decisions
- De-duplicates clubs before querying — no point asking about the same team twice.
- Returns fixture with home/away status and which day of the matchday window.
- Falls back gracefully with `opponent: "unknown"` when uncertain.
