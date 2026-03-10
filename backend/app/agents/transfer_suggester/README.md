# Transfer Suggester Agent

## What This Is

Suggests 1-2 alternative transfers for players flagged as RISK or BENCH.

## Design Decisions

- Only processes at-risk players — no wasted tokens on starters.
- Alternatives must be at the same position and within ±1.0 price.
- Prioritises nailed starters with favourable upcoming fixtures.
