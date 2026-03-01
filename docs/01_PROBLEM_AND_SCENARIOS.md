# ucl-fantasy-scout — Problem & Scenarios

## Overview

UCL Fantasy managers need to make informed squad decisions before each matchday deadline. Currently, this requires manually searching for team news, injury updates, lineup previews, fixture difficulty, and recent match stats across multiple sources — a time-consuming and error-prone process with no single trusted tool.

This app automates that research pipeline. The user uploads a screenshot of their UCL Fantasy squad and receives a detailed AI-generated report covering starter probability, bench risk, and smart transfer suggestions — all grounded in the most recent available news and data.

---

## The Core Problem

### Primary Question (Must Answer Well)

> **Who in my squad is likely to start vs. be benched or rotated for this matchday?**

### Secondary Question

> **Should I transfer anyone out, and if so, who should I bring in at a similar price?**

### Why This Is Hard

This is not a simple lookup. There are many interacting signals — form, rotation cycles, minutes played, squad depth, fixture timing, injury rumours — and experienced managers weigh them differently depending on context. The research process involves judgment calls, not just data retrieval. A wrong matchday alone can invalidate the entire analysis.

---

## Critical Constraint: Matchday Identification

**The matchday must be correctly identified before any analysis begins. This is the single most important prerequisite.**

- If the matchday is wrong, all lineup predictions will be based on the wrong fixtures — making the entire output useless or actively harmful
- The matchday should be extracted from the uploaded squad screenshot
- If it cannot be clearly determined from the image, the app **must ask the user** to confirm or enter it manually before proceeding
- The system should also confirm the matchday with the user as a sanity check even when it believes it has identified it correctly

---

## Timing Matters

- **Ideal time to use this app: the day before the matchday deadline**
- Predictions made earlier than 48 hours before kickoff are unlikely to be reliable — official lineups, injury updates, and rotation decisions are rarely known that far in advance
- The app should surface a warning if the user is running analysis significantly ahead of the matchday window
- The most recent news (last 7 days) is what matters. Older news should be deprioritised or ignored

---

## Understanding the Squad Structure

### Main Squad + Substitutes

- A UCL Fantasy squad includes both starting players and substitutes
- Substitutes matter — if a substitute does not play, the user loses points
- The app must analyse the full squad including subs, not just the starting XI
- The user needs to know if it is worth swapping a sub into the main squad or vice versa

### Multi-Day Matchdays

- A single UCL matchday typically spans **2 days** (e.g. Tuesday + Wednesday)
- Players are locked in before the first game of that matchday — the user cannot change their squad between Day 1 and Day 2
- This means the analysis must account for **all fixtures across both days** of the matchday, not just the first day
- A player playing on Day 2 but not Day 1 should not be misread as a non-starter

---

## How The Manual Research Process Works (Reference for AI Behaviour)

This is how an experienced manager currently does this research manually. The AI should replicate and automate this workflow:

### Step 1 — Identify the Matchday and Fixtures

- Confirm which matchday is coming up
- For each player in the squad, identify which club they play for and who that club is playing against in the UCL matchday

### Step 2 — Search for Match Preview

- Search: `[Team A] vs [Team B] preview` — e.g. `Barcelona vs Inter Milan preview`
- Focus on the **most recent articles only** (last 7 days)
- Key sources to prioritise:
  - **Sportsmole** — publishes expected/predicted lineups before UCL games, generally reliable
  - Major football news outlets with lineup coverage
- From preview articles, extract: expected starting XI, injury news, rotation hints

### Step 3 — Validate With Recent Match History

- Check the last few matches of the player's club
- Confirm whether the target player featured and for how many minutes:
  - **90 minutes in recent match + squad rotation options available** → possible bench risk
  - **30 minutes or less in recent match** → likely being saved/managed for UCL → positive indicator
  - **Not in squad / not on bench recently** → injury or out of favour concern

### Step 4 — Cross-Reference Stats

- Check league and UCL stats for the player: goals, assists, clean sheets, minutes played
- Key player articles (e.g. "Top picks for Matchday X") are useful signals — players frequently highlighted are usually nailed starters
- Recent form is more important than season totals

### Step 5 — Form a Verdict

- Synthesise all the above into: **START ✅ / RISK ⚠️ / BENCH ❌**
- Include a short explanation of the reasoning
- For RISK and BENCH players, suggest 1–2 alternatives at a similar fantasy price

> **Note:** Even with all this research, predictions are not always correct. The goal is to make an informed, well-reasoned estimate — not a guarantee. The app should communicate uncertainty clearly.

---

## UCL Fantasy Rules Reference

The app and its agents should be aware of official UCL Fantasy rules:

📖 [Official UCL Fantasy Rules 2025–26](https://www.uefa.com/uefachampionsleague/news/025f-0fd4b42cc0a7-74498b7df63b-1000--uefa-champions-league-fantasy-football-rules-2025-26/)

Key rule areas that affect analysis:

- Scoring system (goals, assists, clean sheets, bonus points)
- Transfer rules and deadlines per matchday
- Captain and vice-captain scoring multipliers
- Substitution rules and bench point logic

The backend should scrape or cache a summary of these rules to inform agent decisions.

---

## Ad Hoc Research Mode

Beyond the automated squad analysis, users should be able to ask the AI free-form research questions, for example:

- _"Is Vinicius Jr likely to start on Tuesday?"_
- _"Which midfielders under €9m are nailed for Matchday 6?"_
- _"How has Salah performed in UCL this season?"_

This is a secondary feature but potentially the most valuable for power users — a conversational research assistant backed by real-time web search.

---

## Testing Approach

### The Matchday Testing Problem

Testing this app normally requires waiting for an active matchday — which is impractical during development.

**Solution: Historical matchday testing mode**

- Allow the user to upload a screenshot from a **previous matchday** (where scores and lineups are already known)
- The system treats it as if it were a new upcoming matchday
- After analysis, the developer can compare predicted statuses against what actually happened
- This allows logic validation without waiting for a live matchday
- This mode should be clearly labelled in the UI so developers know they are in test mode

---

## User Scenarios

### Scenario 1 — Standard Pre-Matchday Check

> Sarah has 15 players in her UCL squad. It is the day before Matchday 5. She opens the app (installed as a PWA on her iPhone), takes a screenshot of her squad, and pastes it in. The app identifies Matchday 5 and asks her to confirm. She confirms. The system searches for preview articles and recent match data, then returns a full squad report. Her striker is flagged as RISK because he played 90 minutes in a weekend Premier League fixture and the club has a capable replacement. The app suggests a reliable alternative. Sarah makes the transfer before the deadline.

### Scenario 2 — Matchday Cannot Be Identified

> James uploads a cropped screenshot where the matchday indicator is not visible. The app cannot determine the matchday from the image. It asks: _"We could not confirm the matchday from your screenshot. Could you tell us which matchday this is?"_ James types "Matchday 4" and the analysis proceeds correctly.

### Scenario 3 — Substitute Analysis

> Priya has a midfielder in her substitute slot. The app flags that this player is likely to start for his club, suggesting she should consider swapping him into her main squad and benching a player with a higher rotation risk. The analysis covers the full squad, not just the starting XI.

### Scenario 4 — Multi-Day Fixture Awareness

> David's squad has players from clubs playing on both Tuesday and Wednesday of the matchday. The app groups analysis by day and notes: _"These players are locked in once Tuesday's games kick off — ensure your captain choice accounts for players on Day 2 if Day 1 options are uncertain."_

### Scenario 5 — Historical / Developer Testing Mode

> A developer uploads a Matchday 3 screenshot (already completed). The system analyses it as if it were upcoming, returning START/RISK/BENCH verdicts. The developer then compares the predictions against what actually happened to validate and tune the logic.

### Scenario 6 — API Key Configuration

> A developer sets their Anthropic and Google Gemini API keys in the `.env` file before building the app. In the settings panel, the keys show as _"Configured via environment"_ and are masked. A non-technical user opens the deployed app and enters their own key via the settings UI — it is encrypted before being stored in the session.

### Scenario 7 — Ad Hoc Research

> A user has already reviewed their squad report but wants to dig deeper. They type: _"Can you check if Raphinha is likely to start for Barcelona in the UCL this week?"_ The AI performs a targeted web search and returns a concise answer with sources.

---

## Out of Scope (V1)

- User accounts or persistent login
- Saving analysis history across sessions
- Live scores or in-game tracking
- Direct integration with the official UCL Fantasy API
- Push notifications for team news
- Transfer budget optimisation across the full squad
