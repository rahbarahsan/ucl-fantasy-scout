# Preview Researcher Agent

## What This Is

Searches the web for match preview articles and extracts expected lineups,
injury news, and rotation hints for each UCL fixture.

## Design Decisions

- Prioritises Sportsmole as the primary source for predicted lineups.
- Restricts search to the last 7 days for relevance.
- When no SerpAPI key is available, relies on the AI provider's own knowledge.
- Compiles web search context and passes it to the AI for structured extraction.
