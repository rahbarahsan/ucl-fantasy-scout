# ucl-fantasy-scout — Code Structure

## Tech Stack

| Layer               | Choice                                                       |
| ------------------- | ------------------------------------------------------------ |
| Frontend Framework  | React 18 + Vite                                              |
| Frontend Language   | TypeScript                                                   |
| Styling             | Tailwind CSS v3                                              |
| PWA                 | vite-plugin-pwa                                              |
| Backend Framework   | Python + FastAPI                                             |
| Agent Orchestration | Custom async agent pipeline (LangGraph considered for V2)    |
| AI Providers        | Anthropic Claude, Google Gemini                              |
| Web Search          | Provider-native tool use / SerpAPI                           |
| API Key Storage     | Encrypted in-session (frontend) + `.env` (backend pre-build) |
| Containerisation    | Docker + Docker Compose                                      |
| CI/CD               | GitHub Actions                                               |
| Linting (Frontend)  | ESLint, Prettier, npm audit                                  |
| Linting (Backend)   | Pylint, Black, Flake8, detect-secrets                        |
| Testing (Frontend)  | Vitest, React Testing Library, Playwright (E2E)              |
| Testing (Backend)   | Pytest, pytest-asyncio, httpx (E2E)                          |

---

## Why a Custom Agent Pipeline (Not CrewAI / LangGraph)

The research workflow involves many interacting signals: fixture lookup, lineup previews, recent match history, player stats, and rotation logic. This is too complex for a single prompt but does not yet require a full multi-agent debate framework.

**V1 approach:** A custom sequential async pipeline in FastAPI — each agent is a focused async function with a clear input/output contract. This keeps the system transparent, debuggable, and fast to iterate on.

**V2 consideration:** If agent coordination becomes complex (e.g. agents verifying each other, parallel research tasks, self-healing retry loops), migrate to LangGraph.

### Agent Pipeline Overview

```
Image Upload
    │
    ▼
[Agent 1] Squad Parser          → Extract players + positions from image
    │                              Flag if matchday cannot be identified
    ▼
[Agent 2] Matchday Validator    → Confirm/resolve matchday (ask user if unclear)
    │
    ▼
[Agent 3] Fixture Resolver      → For each player: find their club's UCL opponent
    │
    ▼
[Agent 4] Preview Researcher    → Web search: "[Team] vs [Opponent] preview"
    │                              Prioritise Sportsmole + major outlets
    │                              Restrict to last 7 days
    ▼
[Agent 5] Form Analyser         → Check recent match history per player
    │                              Minutes played, rotation signals
    ▼
[Agent 6] Stats Collector       → UCL + league stats: goals, assists, clean sheets
    │
    ▼
[Agent 7] Verdict Engine        → Synthesise all signals → START / RISK / BENCH
    │                              Generate reasoning + confidence level
    ▼
[Agent 8] Transfer Suggester    → For RISK/BENCH: suggest alternatives at similar price
    │
    ▼
Final Report JSON
```

> **Note on image parsing:** Squad screenshots can vary significantly in format, layout, and resolution depending on the device and app version. Agent 1 must be robust to this — do not assume a fixed layout. Use vision-capable models (Claude or Gemini) and validate extracted data before proceeding.

---

## Repository Structure

```
ucl-fantasy-scout/
│
├── frontend/                          # React + Vite + TypeScript + Tailwind
├── backend/                           # FastAPI + Python agent pipeline
├── database/                          # DB schemas, migrations (future use)
├── docker/                            # Dockerfiles for frontend and backend
├── .ci/                               # GitHub Actions, linting configs
├── docs/                              # Top-level project documentation
│   ├── ARCHITECTURE.md               # System design and agent flow diagrams
│   ├── CONTRIBUTING.md               # How to contribute
│   ├── DEPLOYMENT.md                 # Docker, env setup, production notes
│   └── ENV_SETUP.md                  # Step-by-step guide for all environment variables
├── docker-compose.yml
├── .env.example
└── README.md                          # Attractive, professional, GitHub stars-focused
```

---

## Frontend Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   └── icons/                         # PWA icons (192x192, 512x512)
│
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   │
│   ├── types/
│   │   └── index.ts                   # All shared TypeScript interfaces
│   │
│   ├── constants/
│   │   └── providers.ts               # Provider labels, supported models
│   │
│   ├── hooks/
│   │   ├── useImageUpload.ts          # File picker, drag & drop, clipboard paste
│   │   ├── useAnalysis.ts             # Triggers backend API, manages state
│   │   └── useAdHocResearch.ts        # Free-form AI research chat
│   │
│   ├── services/
│   │   └── api.ts                     # All calls to FastAPI backend (no direct AI calls from frontend)
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   └── Header.tsx
│   │   │
│   │   ├── settings/
│   │   │   ├── ProviderSelector.tsx   # Claude / Gemini switcher
│   │   │   └── ApiKeyInput.tsx        # Key input with encryption, env detection
│   │   │
│   │   ├── upload/
│   │   │   └── SquadUploader.tsx      # Upload zone: file, drag & drop, paste
│   │   │
│   │   ├── matchday/
│   │   │   └── MatchdayConfirm.tsx    # Dialog to confirm or enter matchday manually
│   │   │
│   │   ├── results/
│   │   │   ├── ResultsSummary.tsx     # START / RISK / BENCH count badges
│   │   │   ├── PlayerGroup.tsx        # Section wrapper per status group
│   │   │   ├── PlayerCard.tsx         # Player card with status, reasoning
│   │   │   ├── StatusBadge.tsx        # Coloured badge component
│   │   │   └── AlternativeCard.tsx    # Transfer suggestion card
│   │   │
│   │   ├── research/
│   │   │   └── AdHocChat.tsx          # Free-form research chat interface
│   │   │
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── ErrorBanner.tsx
│   │       ├── LoadingSpinner.tsx
│   │       └── WarningBanner.tsx      # e.g. "Too early to predict reliably"
│   │
│   └── utils/
│       ├── imageToBase64.ts
│       ├── encryptKey.ts              # AES encrypt/decrypt API keys in session
│       └── parseResponse.ts           # Type-safe parsing of backend response
│
├── tests/
│   ├── unit/                          # Vitest unit tests per component/hook/util
│   ├── integration/                   # Component interaction tests
│   └── e2e/                           # Playwright E2E (basic local smoke tests)
│
├── demo/                              # Playwright demo recording scripts
│   ├── record.ts                      # Main script: launches app, runs scripted flow, records
│   ├── scenarios/
│   │   ├── squad_analysis.ts          # Full flow: upload screenshot → analysis results
│   │   └── settings_switch.ts         # Provider switching and key config demo
│   ├── assets/
│   │   └── sample_squad.png           # Sample squad screenshot used in demo recording
│   ├── output/                        # Generated videos and GIFs (gitignored)
│   └── README.md                      # How to run recordings, convert to GIF, adjust quality
│
├── docs/
│   └── FRONTEND.md                    # What this is, how to run, design decisions
│
├── index.html
├── vite.config.ts                     # Vite + PWA plugin config
├── tailwind.config.ts
├── tsconfig.json
├── .eslintrc.cjs
├── .prettierrc
└── package.json
```

---

## Backend Structure

```
backend/
├── app/
│   ├── main.py                        # FastAPI app entry point, router registration
│   ├── config.py                      # Settings, env vars, API key loading
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── analysis.py            # POST /analyse - main squad analysis endpoint
│   │   │   ├── research.py            # POST /research - ad hoc question endpoint
│   │   │   └── health.py              # GET /health
│   │   └── middleware/
│   │       ├── auth.py                # API key validation middleware
│   │       └── rate_limit.py          # Basic rate limiting
│   │
│   ├── agents/                        # Core agent pipeline
│   │   ├── __init__.py
│   │   ├── pipeline.py                # Orchestrator: runs agents in sequence
│   │   │
│   │   ├── squad_parser/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # Extracts players from image using vision AI
│   │   │   ├── prompts.py             # System + user prompts for parsing
│   │   │   └── README.md              # What this agent does, design decisions, how to test
│   │   │
│   │   ├── matchday_validator/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # Confirms matchday, returns clarification request if unclear
│   │   │   ├── prompts.py
│   │   │   └── README.md
│   │   │
│   │   ├── fixture_resolver/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # Maps each player's club to UCL fixture for this matchday
│   │   │   ├── prompts.py
│   │   │   └── README.md
│   │   │
│   │   ├── preview_researcher/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # Web search for match previews and expected lineups
│   │   │   ├── sources.py             # Source priority config (Sportsmole etc.)
│   │   │   ├── prompts.py
│   │   │   └── README.md
│   │   │
│   │   ├── form_analyser/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # Checks recent match history, minutes played
│   │   │   ├── prompts.py
│   │   │   └── README.md
│   │   │
│   │   ├── stats_collector/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # UCL + league stats per player
│   │   │   ├── prompts.py
│   │   │   └── README.md
│   │   │
│   │   ├── verdict_engine/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # Synthesises all signals into START/RISK/BENCH
│   │   │   ├── rules.py               # Heuristic rules (rotation logic, minutes thresholds)
│   │   │   ├── prompts.py
│   │   │   └── README.md
│   │   │
│   │   └── transfer_suggester/
│   │       ├── __init__.py
│   │       ├── agent.py               # Suggests alternatives for RISK/BENCH players
│   │       ├── prompts.py
│   │       └── README.md
│   │
│   ├── providers/                     # AI provider abstraction layer
│   │   ├── __init__.py
│   │   ├── base.py                    # Abstract base class for all providers
│   │   ├── anthropic.py               # Claude integration (vision + text + tool use)
│   │   └── gemini.py                  # Gemini integration (vision + text + tool use)
│   │
│   ├── tools/                         # Tool use / web search wrappers
│   │   ├── web_search.py              # Web search abstraction (provider tool use or SerpAPI)
│   │   └── scraper.py                 # Lightweight scraper for known sources
│   │
│   ├── schemas/                       # Pydantic request/response models
│   │   ├── analysis.py
│   │   └── research.py
│   │
│   └── utils/
│       ├── image.py                   # Base64 decode, format validation, normalisation
│       ├── encryption.py              # API key encrypt/decrypt utilities
│       └── logger.py                  # Structured logging setup
│
├── tests/
│   ├── unit/                          # Per-agent, per-util unit tests with mocks
│   ├── integration/                   # Agent pipeline integration tests
│   └── e2e/                           # Basic end-to-end via httpx against local server
│
├── docs/
│   └── BACKEND.md                     # Overview, how to run, env setup, design decisions
│
├── .env.example
├── requirements.txt
├── requirements-dev.txt               # Test + lint dependencies
├── pyproject.toml                     # Pylint, Black, isort config
└── Dockerfile
```

---

## API Key Management

### Pre-Build Configuration (Developers / Self-Hosters)

- Keys set in `.env` file before build
- Loaded via `config.py` using `pydantic-settings`
- Frontend detects pre-configured keys and shows _"Configured via environment ✅"_
- Pre-configured keys are never sent to the frontend — the backend uses them directly

### Runtime Configuration (End Users)

- Users enter keys in the settings UI
- Keys are **AES-256 encrypted** in the browser session using a session-derived key (`encryptKey.ts`)
- Encrypted key is sent to backend in request headers
- Backend decrypts for use, never logs or persists the key
- Keys are cleared on page refresh

### `.env.example`

```env
# AI Providers
ANTHROPIC_API_KEY=
GEMINI_API_KEY=

# Encryption
ENCRYPTION_SECRET=your-random-32-char-secret

# App
ENVIRONMENT=development
LOG_LEVEL=INFO
```

---

## TypeScript Types (`frontend/src/types/index.ts`)

```ts
export type ProviderKey = "anthropic" | "gemini";
export type PlayerStatus = "START" | "RISK" | "BENCH";

export interface Alternative {
  name: string;
  team: string;
  position: string;
  price: string;
  reason: string;
}

export interface Player {
  name: string;
  position: "GK" | "DEF" | "MID" | "FWD";
  team: string;
  status: PlayerStatus;
  reason: string;
  confidence: "HIGH" | "MEDIUM" | "LOW";
  price: string;
  isSubstitute: boolean;
  alternatives: Alternative[];
}

export interface AnalysisResult {
  matchday: string;
  matchdayConfirmed: boolean;
  analysisDay: "DAY_1" | "DAY_2" | "BOTH";
  earlyWarning: boolean; // true if too early to predict reliably
  players: Player[];
}
```

---

## Testing Strategy

### Philosophy

- **Unit tests:** Test each agent function and utility in isolation using mocks for AI provider calls and web search. These run in CI on every push.
- **Integration tests:** Test the full agent pipeline with mocked external calls. Validate that agents pass correct data between each other.
- **E2E tests:** Basic smoke tests against the locally running server. Designed to be run manually before a release, not in CI (due to live API calls and cost).

### Test Structure

Each agent submodule has its own test file:

```
tests/unit/agents/test_squad_parser.py
tests/unit/agents/test_verdict_engine.py
tests/unit/utils/test_encryption.py
tests/integration/test_pipeline.py
tests/e2e/test_full_analysis.py
```

### Frontend Testing

```
tests/unit/hooks/useImageUpload.test.ts
tests/unit/components/PlayerCard.test.tsx
tests/integration/SquadUploader.test.tsx
tests/e2e/analysis_flow.spec.ts         # Playwright
```

---

## CI/CD (`.ci/` Folder)

```
.ci/
├── workflows/
│   ├── ci.yml                         # Runs on every PR: lint + unit + integration tests
│   └── release.yml                    # Runs on merge to main: build + Docker push
├── pylintrc                           # Pylint configuration (line limit, ignored rules, etc.)
├── .flake8                            # Flake8 configuration (max-line-length=88 to match Black)
├── pyproject.toml                     # Black configuration (line-length=88, target Python version)
├── .isort.cfg                         # Import ordering consistent with Black
├── .prettierrc                        # Prettier configuration
├── .eslintrc.cjs                      # ESLint configuration
└── .secrets.baseline                  # detect-secrets baseline file
```

### CI Pipeline Steps (`ci.yml`)

1. **detect-secrets** — scan for accidentally committed API keys or secrets
2. **Black + Pylint + Flake8** — Python formatting and linting
3. **ESLint + Prettier** — TypeScript/React linting
4. **npm audit** — frontend dependency vulnerability check
5. **pip-audit** — Python dependency vulnerability check
6. **Pytest (unit + integration)** — backend tests with mocks
7. **Vitest (unit + integration)** — frontend tests

---

## Docker Setup

```yaml
# docker-compose.yml
services:
  backend:
    build: ./docker/backend
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./backend:/app

  frontend:
    build: ./docker/frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
```

Run everything locally with:

```bash
cp .env.example .env
# Fill in your API keys in .env
docker-compose up --build
```

---

## Prototyping Approach

To validate agent logic quickly without waiting for a live matchday:

1. Use historical matchday screenshots as test inputs (see Scenario 5 in problem doc)
2. Each agent can be tested in isolation via a simple CLI script under `backend/scripts/` — e.g. `python scripts/test_squad_parser.py --image samples/matchday3.png`
3. Keep a `PROTOTYPE_LOG.md` in `docs/` tracking what was tried, what worked, and what was changed — this forms the basis for the final architecture cleanup

---

### Documentation Standards

Every module and submodule must have a `README.md` or doc file covering:

- **What this is** — purpose and responsibility
- **How to run** — commands, venv activation, dependencies, environment requirements
- **Design decisions** — why this approach was chosen over alternatives
- **Known limitations** — edge cases or things not handled yet

### `docs/ENV_SETUP.md`

A dedicated, beginner-friendly guide covering:

- What each environment variable does and where to get its value
- How to create `.env` from `.env.example`
- How to get an Anthropic API key (link to console.anthropic.com)
- How to get a Gemini API key (link to Google AI Studio)
- What `ENCRYPTION_SECRET` is and how to generate a secure one (`openssl rand -hex 32`)
- Which variables are required vs optional
- What happens if a variable is missing (expected error message)
- How pre-configured keys appear in the UI vs runtime-entered keys

---

## Coding Conventions

### File Size Limit

- **No file should exceed 600 lines** — this is a hard rule, not a guideline
- If a file approaches this limit, break it into logical submodules (e.g. split `agent.py` into `agent.py` + `helpers.py` + `prompts.py`)
- This keeps files readable, maintainable, and AI-assistant friendly (Copilot context degrades on large files)

### Python (Backend)

- All agents are async functions
- Pydantic models for all inputs and outputs
- No `print()` — use structured logger
- Type hints on all function signatures
- No API keys in logs under any circumstance
- Code must be written to be **Pylint and Black compliant from the start** — do not write code and fix linting afterwards
  - Use Black-compatible formatting: 88 char line length, double quotes, trailing commas
  - Avoid Pylint warnings by design: name variables clearly, avoid too-many-arguments (use dataclasses/Pydantic instead), avoid too-many-branches (split into functions)
  - Where a Pylint rule genuinely cannot be avoided (e.g. broad exception handling at pipeline boundaries), use targeted inline suppression with a comment explaining why:
    ```python
    except Exception as exc:  # pylint: disable=broad-except
        # Broad catch intentional here — pipeline must not crash on agent failure
        logger.error("Agent failed: %s", exc)
    ```
  - Never suppress Pylint errors wholesale — only inline and only where justified
- **Always use a Python virtual environment**
  - Every `README.md` and doc that involves running Python code must include venv creation and activation as the first step
  - Never run `pip install` outside a virtual environment
  - The venv folder (`venv/`, `.venv/`) must be in `.gitignore`

### TypeScript (Frontend)

- Named exports only
- Props interfaces co-located with components
- No `any` — use `unknown` with type guards
- Tailwind classes only — no inline styles
- All async functions use `try/catch` with typed errors
- ESLint and Prettier compliant from the start — same philosophy as Python: write clean, don't fix later

---

## Getting Started

### Local Development (Without Docker)

```bash
# Backend — always activate venv first
cd backend
python -m venv venv
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env              # See docs/ENV_SETUP.md for all variables
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Local Development (With Docker)

```bash
cp .env.example .env
docker-compose up --build
```

### Run Tests

```bash
# Backend
cd backend && pytest tests/unit tests/integration

# Frontend
cd frontend && npm run test
```

### Record Demo Video / GIF

```bash
cd frontend
npm run demo:record          # Runs Playwright demo script, outputs .webm to demo/output/
npm run demo:gif             # Converts .webm → .gif using ffmpeg (must be installed)
```

The demo scripts simulate a real user flow with realistic typing speed, hover states, and scroll behaviour — producing a polished recording suitable for the README or a landing page. Output files are gitignored; only committed manually when ready to update the README assets.

### GIF Quality & Size Guide for GitHub READMEs

**GitHub limits:** Max file size is **10MB** per file. GIFs above this will not render inline.

**Recommended settings:**
| Setting | Value |
|---|---|
| Viewport | 1280×800 (widescreen, crisp on retina) |
| Duration | 20–40 seconds max (longer = bigger file) |
| FPS | 15fps for GIF (24fps for .webm/video) |
| Colour palette | 128 colours (good quality, smaller size) |
| Output width | Scale down to 900px wide for README embed |

**ffmpeg conversion command (produces sharp, small GIF):**

```bash
# Step 1: Generate optimised palette
ffmpeg -i demo/output/recording.webm -vf "fps=15,scale=900:-1:flags=lanczos,palettegen=max_colors=128" demo/output/palette.png

# Step 2: Convert using palette
ffmpeg -i demo/output/recording.webm -i demo/output/palette.png \
  -vf "fps=15,scale=900:-1:flags=lanczos,paletteuse=dither=bayer" \
  demo/output/demo.gif
```

**Embedding in README:**

```markdown
<p align="center">
  <img src="docs/assets/demo.gif" alt="UCL Fantasy Assistant Demo" width="900" />
</p>
```

> Tip: If the GIF exceeds 10MB, reduce duration first, then drop FPS to 12, then reduce scale to 800px. Avoid reducing colour palette below 64 as it looks poor.

### Run Linters

```bash
# Backend
black . && pylint app/ && flake8 app/

# Frontend
npm run lint && npm run format:check

# Secrets scan
detect-secrets scan --baseline .ci/.secrets.baseline
```
