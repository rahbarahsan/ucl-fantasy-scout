# Backend Setup & Architecture

## Overview

The backend is a **FastAPI server** with a custom 8-agent pipeline for analyzing UCL Fantasy squads. Each agent is an async function with a clear responsibility, collectively extracting player data, researching fixtures, analyzing form, and providing verdicts.

---

## Tech Stack

- **Runtime:** Python 3.11
- **Web Framework:** FastAPI 0.115.6
- **Async Runtime:** asyncio
- **Data Validation:** Pydantic 2.10.4
- **AI Providers:** Anthropic Claude Sonnet 4, Google Gemini 2.0 Flash
- **Image Processing:** Pillow 12.1.1 (PIL.Image)
- **Encryption:** cryptography (AES-256)
- **Logging:** structlog
- **HTTP Client:** httpx
- **Testing:** pytest 8.3.4, pytest-asyncio

---

## Project Structure

```
backend/
├── app/
│   ├── agents/
│   │   ├── squad_parser.py          # Agent 1: Extract players from image
│   │   ├── matchday_validator.py    # Agent 2: Confirm matchday
│   │   ├── fixture_resolver.py      # Agent 3: Find opponents
│   │   ├── preview_researcher.py    # Agent 4: Research upcoming matches
│   │   ├── form_analyser.py         # Agent 5: Gather player form data
│   │   ├── stats_collector.py       # Agent 6: Collect stats (goals, assists, mins)
│   │   ├── verdict_engine.py        # Agent 7: Generate START/RISK/BENCH verdicts
│   │   └── transfer_suggester.py    # Agent 8: Recommend transfers
│   │
│   ├── api/
│   │   ├── routes.py                # API endpoints
│   │   ├── middleware.py            # Auth & rate limiting
│   │   └── decorators.py            # Helper decorators
│   │
│   ├── providers/
│   │   ├── base.py                  # Abstract AIProvider
│   │   ├── anthropic.py             # Claude implementation
│   │   └── gemini.py                # Gemini implementation
│   │
│   ├── schemas/
│   │   ├── agent.py                 # Agent input/output Pydantic models
│   │   ├── api.py                   # API request/response models
│   │   └── utils.py                 # Shared schemas (Player, Position, etc.)
│   │
│   ├── tools/
│   │   ├── web_search.py            # Web search abstraction
│   │   └── scraper.py               # HTML scraping utility
│   │
│   ├── utils/
│   │   ├── logger.py                # Structured logging setup
│   │   ├── encryption.py            # AES-256 encryption/decryption
│   │   ├── image.py                 # Image validation & Base64 conversion
│   │   └── constants.py             # App constants
│   │
│   ├── config.py                    # Settings (Pydantic)
│   ├── main.py                      # FastAPI app initialization
│   └── pipeline.py                  # Agent orchestrator
│
├── tests/
│   ├── unit/
│   │   ├── test_agents.py           # Agent logic tests
│   │   └── test_utils.py            # Utility function tests
│   ├── integration/
│   │   └── test_pipeline.py         # Full pipeline integration test
│   └── e2e/
│       └── test_full_analysis.py    # End-to-end API tests (uses real API keys)
│
├── Dockerfile
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- pip or uv

### Local Development

1. **Clone & navigate:**
   ```bash
   git clone https://github.com/rahbarahsan/ucl-fantasy-scout.git
   cd ucl-fantasy-scout/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   Server starts at `http://localhost:8000`
   - API docs: `http://localhost:8000/docs` (Swagger)
   - ReDoc: `http://localhost:8000/redoc`

---

## Configuration

### Environment Variables

All configuration is managed via `.env` file. The `config.py` uses **Pydantic Settings** for validation.

| Variable | Required | Type | Description | Example |
|----------|----------|------|-------------|---------|
| `ANTHROPIC_API_KEY` | Yes* | str | Claude API key | `sk-ant-...` |
| `GEMINI_API_KEY` | Yes* | str | Gemini API key | `AIza...` |
| `ENCRYPTION_SECRET` | Yes | str | AES-256 key (32+ chars) | `my-secret-key-32-characters!!` |
| `SERPAPI_KEY` | No | str | SerpAPI for real web search | `abc123def456...` |
| `ENVIRONMENT` | No | str | `development` or `production` | `development` |
| `LOG_LEVEL` | No | str | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |

\* At least one AI provider key is required.

### Loading `.env`

The config file resolves `.env` from the **project root** (3 levels up from `app/config.py`):

```python
from pathlib import Path
env_path = Path(__file__).parent.parent.parent / ".env"
```

This works both locally and in Docker.

---

## Core Components

### 1. AI Provider Abstraction

**File:** `app/providers/base.py`

```python
class AIProvider(ABC):
    """Abstract base for AI providers (Claude, Gemini)."""
    
    async def generate_text(
        self, 
        prompt: str, 
        system: str | None = None,
        temperature: float = 0.7
    ) -> str:
        """Generate text response."""
        pass
```

**Implementations:**
- `AnthropicProvider` — Wraps Claude Sonnet 4, uses tool_use for web searches
- `GeminiProvider` — Wraps Gemini 2.0 Flash, uses function_calling

### 2. Agent Pipeline (8 Sequential Agents)

**File:** `app/pipeline.py`

Each agent is an async function that receives the previous agent's output and yields its result.

```python
async def run_analysis_pipeline(
    squad_image_base64: str,
    provider_name: str = "anthropic"
) -> AnalysisResult:
    """Orchestrate 8-agent pipeline."""
```

**Agent Sequence:**

1. **Squad Parser** (`squad_parser.py`)
   - Input: Base64 image
   - Output: List of players with positions, matchday guess
   - Logic: Vision call to extract player names from screenshot

2. **Matchday Validator** (`matchday_validator.py`)
   - Input: Players, matchday guess
   - Output: Confirmed matchday
   - Logic: Ask user to confirm if uncertain

3. **Fixture Resolver** (`fixture_resolver.py`)
   - Input: Players, matchday
   - Output: Players + opponent mappings
   - Logic: Web search to find UCL fixtures for the matchday

4. **Preview Researcher** (`preview_researcher.py`)
   - Input: Players, fixtures
   - Output: Players + preview data (lineups, injuries)
   - Logic: Search for "[Team] vs [Opponent] preview"

5. **Form Analyser** (`form_analyser.py`)
   - Input: Players, recent matches
   - Output: Players + form scores
   - Logic: Analyze recent performance trends

6. **Stats Collector** (`stats_collector.py`)
   - Input: Players, season stats
   - Output: Players + season stats (goals, assists, minutes)
   - Logic: Aggregate season data

7. **Verdict Engine** (`verdict_engine.py`)
   - Input: Players + all research data
   - Output: Verdicts (START/RISK/BENCH)
   - Logic: Decision rules based on fixtures, form, rotation risk

8. **Transfer Suggester** (`transfer_suggester.py`)
   - Input: Players + verdicts
   - Output: Transfer recommendations
   - Logic: Find alternatives at similar price for RISK/BENCH players

---

## API Endpoints

### `/health` (GET)

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### `/api/analyse` (POST)

Analyze a squad screenshot through the full 8-agent pipeline.

**Request:**
```json
{
  "image_base64": "data:image/png;base64,iVBORw0KG...",
  "provider": "anthropic"
}
```

**Response:**
```json
{
  "matchday": 6,
  "analysis_quality": "HIGH",
  "players": [
    {
      "name": "Harry Kane",
      "position": "FWD",
      "opponent": "Barcelona",
      "verdict": "START",
      "confidence": 0.95,
      "reasoning": "Strong fixture, excellent form",
      "suggested_transfer": null
    },
    ...
  ],
  "summary": "Strong squad for MD6. Consider rotating Kane for deeper differential."
}
```

---

### `/api/research` (POST)

Ad-hoc research question endpoint.

**Request:**
```json
{
  "question": "Which teams are resting players in the Group Stage?",
  "provider": "anthropic"
}
```

**Response:**
```json
{
  "answer": "Based on recent reports...",
  "sources": [
    {
      "title": "UCL Team Resting Plans",
      "url": "https://...",
      "snippet": "Several teams..."
    }
  ],
  "confidence": "HIGH"
}
```

---

## Middleware & Security

**File:** `app/api/middleware.py`

1. **API Key Authentication:** X-API-Key header, decrypted server-side
2. **Rate Limiting:** 10 requests per minute per IP
3. **CORS:** Configured for frontend origin
4. **Error Handling:** Structured error responses

---

## Testing

### Unit Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/unit/ -v
```

**Coverage:**
- `test_agents.py` — JSON parsing, agent logic
- `test_utils.py` — Encryption, image validation

### Integration Tests

```bash
pytest tests/integration/ -v
```

**Coverage:**
- `test_pipeline.py` — Full pipeline with mocked providers

### E2E Tests (Local only)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
pytest tests/e2e/ -v
```

**Coverage:**
- `test_full_analysis.py` — Real API calls, error handling

---

## Logging

**File:** `app/utils/logger.py`

Uses `structlog` for structured JSON logging:

```python
from app.utils.logger import get_logger

log = get_logger(__name__)
log.info("event", player_count=10, matchday=6)
```

**Output:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "event": "event",
  "player_count": 10,
  "matchday": 6
}
```

---

## Deployment

### Docker

```bash
# Build
docker build -t ucl-fantasy-scout-backend:latest .

# Run
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e GEMINI_API_KEY=AIza... \
  -e ENCRYPTION_SECRET=... \
  ucl-fantasy-scout-backend:latest
```

### Docker Compose

```bash
docker compose up backend
```

---

## Troubleshooting

### Common Issues

1. **`.env` file not loading**
   - Ensure `.env` is in the project root, not `backend/`
   - Verify file is readable: `ls -la .env`

2. **Image validation fails**
   - Check image is valid Base64
   - Supported formats: PNG, JPEG, WebP, GIF
   - Max size: 20MB

3. **API key errors**
   - Verify `ANTHROPIC_API_KEY` or `GEMINI_API_KEY` is set
   - Test key validity with provider's CLI

4. **Rate limiting errors**
   - Backend returns 429 (Too Many Requests)
   - Wait 60 seconds before next request

---

## Next Steps

- [ ] Add database for squad history persistence
- [ ] Implement caching layer for fixture/form data
- [ ] Add webhook support for external integrations
- [ ] Migrate to LangGraph for V2 if agent complexity increases
