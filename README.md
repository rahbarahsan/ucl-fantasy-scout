# UCL Fantasy Scout

An AI-powered analysis tool for **UEFA Champions League Fantasy Football**. Upload your squad screenshot and receive **START / RISK / BENCH** verdicts for every player — powered by a multi-agent pipeline that researches fixtures, form, rotation risk, and stats in real time.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Features

### 📸 Squad Analysis (Screenshot Upload)
Upload a screenshot of your UCL Fantasy squad and get AI-driven verdicts for every player:
1. **Extract** — Vision AI reads player names and positions from your screenshot
2. **Validate** — Confirms the matchday or asks you to clarify if unclear
3. **Research** — Searches for upcoming fixtures, injury news, expected lineups, and rotation risks
4. **Analyze** — Gathers form data, stats, and playing time trends
5. **Verdict** — Returns **START** (play safely), **RISK** (check other options), or **BENCH** (high rotation risk) for each player
6. **Suggest** — Recommends transfer alternatives for risky or benched players at similar price points

### 💬 Ad-Hoc Research Chat
Ask any UCL Fantasy question and get sourced answers:
- "Which teams are resting players this round?"
- "Is Haaland fit for the upcoming match?"
- "Who are the top scorers in Group A?"
- Answers powered by Claude/Gemini + optional live web search
- View sources and links for each answer

### 🔧 Core Features
- **8-Agent AI Pipeline** — Squad Parser → Matchday Validator → Fixture Resolver → Preview Researcher → Form Analyser → Stats Collector → Verdict Engine → Transfer Suggester
- **Dual AI Provider Support** — Anthropic Claude or Google Gemini (switchable in the UI)
- **Real-Time Research** — Web searches for match previews, injury news, and rotation hints (optional SerpAPI)
- **PWA Support** — Installable on mobile with offline shell caching
- **Client-Side Key Encryption** — API keys are XOR-obfuscated in the browser, AES-256 encrypted server-side

## Architecture

```
┌─────────────────────────────────────┐
│           React Frontend            │
│  (Vite + TypeScript + Tailwind)     │
└──────────────┬──────────────────────┘
               │ POST /api/analyse
               │ POST /api/research
┌──────────────▼──────────────────────┐
│         FastAPI Backend             │
│                                     │
│  ┌─────────────────────────────┐    │
│  │   8-Agent Pipeline          │    │
│  │                             │    │
│  │  1. Squad Parser (vision)   │    │
│  │  2. Matchday Validator      │    │
│  │  3. Fixture Resolver        │    │
│  │  4. Preview Researcher      │    │
│  │  5. Form Analyser           │    │
│  │  6. Stats Collector         │    │
│  │  7. Verdict Engine          │    │
│  │  8. Transfer Suggester      │    │
│  └─────────────────────────────┘    │
│                                     │
│  AI Providers: Claude / Gemini      │
│  Tools: Web Search, Scraper         │
└─────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- An API key for [Anthropic](https://console.anthropic.com/) or [Google AI Studio](https://aistudio.google.com/)

### 1. Clone & configure

```bash
git clone https://github.com/rahbarahsan/ucl-fantasy-scout.git
cd ucl-fantasy-scout
cp .env.example .env
# Edit .env with your API keys
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — the frontend proxies API requests to the backend at :8000.

### Docker (production)

```bash
docker compose up --build
```

Frontend at http://localhost, backend at http://localhost:8000.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes* | Anthropic Claude API key |
| `GEMINI_API_KEY` | Yes* | Google Gemini API key |
| `ENCRYPTION_SECRET` | Yes | 32+ char secret for AES encryption |
| `SERPAPI_KEY` | No | SerpAPI key for real web search |
| `ENVIRONMENT` | No | `development` (default) or `production` |
| `LOG_LEVEL` | No | `DEBUG`, `INFO` (default), `WARNING`, `ERROR` |

\* At least one AI provider key is required.

## Testing

```bash
# Backend
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v

# Frontend unit tests
cd frontend
npm test

# Frontend E2E
npx playwright install
npm run e2e
```

## Project Structure

```
ucl-fantasy-scout/
├── backend/
│   ├── app/
│   │   ├── agents/          # 8 pipeline agents
│   │   ├── api/             # Routes & middleware
│   │   ├── providers/       # AI provider abstractions
│   │   ├── schemas/         # Pydantic models
│   │   ├── tools/           # Web search & scraper
│   │   ├── utils/           # Logger, encryption, image
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # React UI components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API client
│   │   ├── utils/           # Helpers
│   │   ├── types/           # TypeScript types
│   │   └── constants/       # Config constants
│   ├── tests/
│   ├── Dockerfile
│   └── package.json
├── docs/                    # Design documentation
├── docker-compose.yml
└── README.md
```

## License

MIT
