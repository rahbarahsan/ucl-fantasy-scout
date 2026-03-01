# Backend — UCL Fantasy Scout

## What This Is

FastAPI-based backend that runs an 8-agent AI pipeline to analyse UCL Fantasy squad screenshots.

## How to Run

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env           # Fill in API keys
uvicorn app.main:app --reload
```

Server starts at `http://localhost:8000`.

## API Endpoints

| Method | Path             | Description                            |
|--------|------------------|----------------------------------------|
| GET    | `/health`        | Health check + provider status         |
| POST   | `/api/analyse`   | Upload squad screenshot for analysis   |
| POST   | `/api/research`  | Ask a free-form research question      |

## Agent Pipeline

1. **Squad Parser** — Extract players from screenshot (vision AI)
2. **Matchday Validator** — Confirm matchday, ask user if unclear
3. **Fixture Resolver** — Map each club to their UCL fixture
4. **Preview Researcher** — Search web for match previews
5. **Form Analyser** — Check recent match history per player
6. **Stats Collector** — Gather UCL + league statistics
7. **Verdict Engine** — Synthesise signals into START / RISK / BENCH
8. **Transfer Suggester** — Recommend replacements for at-risk players

## Run Tests

```bash
pytest tests/unit tests/integration
```

## Run Linters

```bash
black . && pylint app/ && flake8 app/
```
