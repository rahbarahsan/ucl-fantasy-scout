# Testing Guide

## Overview

This project includes comprehensive testing across **unit**, **integration**, and **end-to-end** layers for both backend and frontend.

---

## Backend Testing

### Setup

```bash
cd backend
pip install -r requirements-dev.txt
```

**Test Dependencies:**

- pytest 8.3.4
- pytest-asyncio
- httpx (for E2E HTTP testing)

---

### Unit Tests

**Location:** `backend/tests/unit/`

Tests isolated functions and classes without external dependencies.

**Run:**

```bash
pytest tests/unit/ -v
```

**Coverage:**

#### `test_agents.py` — Agent Logic

- JSON response parsing (handles markdown fencing)
- Fallback to empty data on parse errors
- Agent input/output contracts

**Example:**

```python
def test_squad_parser_extracts_players():
    """Verify Squad Parser extracts player list from vision."""
    result = parser_agent(squad_image_base64="...")
    assert len(result['players']) > 0
    assert all('name' in p for p in result['players'])
```

#### `test_utils.py` — Utility Functions

- Image validation (PNG/JPEG/WebP/GIF)
- Base64 encoding/decoding
- Encryption (XOR + AES-256)
- Logger initialization

**Example:**

```python
def test_image_validation_rejects_gif():
    """Large GIF should be rejected."""
    invalid_gif = b'GIF89a' + (b'x' * 21_000_000)
    with pytest.raises(ValueError, match="exceeds 20MB"):
        validate_image(invalid_gif)
```

---

### Integration Tests

**Location:** `backend/tests/integration/`

Tests multiple components working together with mocked external dependencies.

**Run:**

```bash
# Run with test API keys
ANTHROPIC_API_KEY=test-key GEMINI_API_KEY=test-key pytest tests/integration/ -v
```

**Coverage:**

#### `test_pipeline.py` — Full Pipeline

- 8-agent pipeline with mocked provider
- Input → Output contract verification
- Error handling between agents
- State persistence through pipeline

**Example:**

```python
@pytest.mark.asyncio
async def test_full_pipeline_with_squad_image():
    """Run full pipeline with mocked provider."""
    result = await run_analysis_pipeline(
        squad_image_base64="base64-encoded-image",
        provider_name="anthropic"
    )
    assert result['matchday'] is not None
    assert len(result['players']) > 0
    assert all(p['verdict'] in ['START', 'RISK', 'BENCH'] for p in result['players'])
```

---

### E2E Tests

**Location:** `backend/tests/e2e/`

Tests real API calls with actual AI providers (uses API quota).

**Run Locally Only:**

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# OR
export GEMINI_API_KEY=AIza...

pytest tests/e2e/ -v
```

**Not run in CI/CD** to preserve API key quota.

**Coverage:**

#### `test_full_analysis.py` — API Endpoints

- POST `/api/analyse` with valid image
- POST `/api/research` with question
- GET `/health` endpoint
- Error handling (invalid image, missing fields)
- Response schema validation

**Example:**

```python
@pytest.mark.asyncio
async def test_analyse_endpoint_with_valid_image():
    """Test full analysis endpoint with real API call."""
    client = TestClient(app)
    response = client.post(
        "/api/analyse",
        json={
            "image_base64": valid_squad_image_base64,
            "provider": "anthropic"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert 'matchday' in data
    assert 'players' in data
```

---

### Run All Backend Tests

```bash
# Unit + Integration only (CI/CD)
pytest tests/ --ignore=tests/e2e -v

# All tests including E2E (local only)
pytest tests/ -v --tb=short
```

**Output Example:**

```
tests/unit/test_agents.py::test_squad_parser_extracts_players PASSED
tests/unit/test_utils.py::test_image_validation_rejects_gif PASSED
tests/integration/test_pipeline.py::test_full_pipeline_with_squad_image PASSED
tests/e2e/test_full_analysis.py::test_analyse_endpoint_with_valid_image PASSED

========================= 24 passed in 2.65s =========================
```

---

## Frontend Testing

### Setup

```bash
cd frontend
npm install
```

**Test Dependencies:**

- vitest 2.1.9
- @testing-library/react
- @testing-library/user-event
- jsdom (for DOM simulation)

---

### Unit Tests

**Location:** `frontend/tests/`

Tests components and utility functions.

**Run:**

```bash
npm test -- --run  # Single run
npm test           # Watch mode
```

**Coverage:**

#### `components/PlayerCard.test.tsx`

- Renders player verdict card
- Displays all required fields (name, position, verdict, confidence)
- Shows transfer suggestion when present
- Applies correct styling for verdict status

**Example:**

```typescript
it('renders player card with START verdict', () => {
  const { getByText } = render(
    <PlayerCard player={{
      name: 'Harry Kane',
      position: 'FWD',
      opponent: 'Barcelona',
      verdict: 'START',
      confidence: 0.95,
      reasoning: 'Strong fixture'
    }} />
  );

  expect(getByText('Harry Kane')).toBeInTheDocument();
  expect(getByText('START')).toBeInTheDocument();
});
```

#### `components/StatusBadge.test.tsx`

- Renders correct color for each status
- Shows confidence percentage
- Handles missing confidence gracefully

**Example:**

```typescript
it('applies correct color for RISK status', () => {
  const { container } = render(<StatusBadge status="RISK" />);
  expect(container.firstChild).toHaveClass('bg-yellow-100');
});
```

#### `hooks/useImageUpload.test.ts`

- Handles file upload
- Validates file size (max 20MB)
- Validates file format (PNG/JPEG/WebP/GIF)
- Converts to Base64
- Clears state

**Example:**

```typescript
it("rejects file over 20MB", async () => {
  const { result } = renderHook(() => useImageUpload());
  const largeFile = new File(["x".repeat(21_000_000)], "big.png", {
    type: "image/png",
  });

  await result.current.uploadImage(largeFile);

  expect(result.current.error).toContain("exceeds 20MB");
});
```

#### `utils/parseResponse.test.ts`

- Parses JSON from markdown code blocks
- Handles plain JSON
- Returns null on parse errors
- Extracts data between triple backticks

**Example:**

````typescript
it("parses JSON from markdown fencing", () => {
  const markdown = '```json\n{"key": "value"}\n```';
  const result = parseResponse(markdown);
  expect(result).toEqual({ key: "value" });
});
````

---

### E2E Tests (Playwright)

**Location:** `frontend/tests/e2e/` and `playwright.config.ts`

Tests full user workflows in a real browser.

**Install Playwright:**

```bash
npx playwright install
```

**Run:**

```bash
# Headless mode
npx playwright test

# Headed mode (browser visible)
npx playwright test --headed

# Debug mode (step-by-step)
npx playwright test --debug

# Specific file
npx playwright test examples.spec.ts
```

**Coverage:**

#### `examples.spec.ts`

- Upload squad screenshot
- Confirm matchday
- View analysis results
- Ask research question
- Configure API key
- Error handling (invalid image, network errors)

**Example:**

```typescript
test("full squad analysis flow", async ({ page }) => {
  await page.goto("http://localhost:5173");

  // Upload image
  await page.setInputFiles('input[type="file"]', "squad.png");
  await page.click('button:has-text("Analyze")');

  // Wait for results
  await page.waitForSelector('[data-testid="player-card"]');

  // Verify verdict
  const verdict = await page
    .locator('[data-testid="verdict"]')
    .first()
    .textContent();
  expect(["START", "RISK", "BENCH"]).toContain(verdict);
});
```

---

### Run All Frontend Tests

```bash
# Unit tests only
npm test -- --run

# Unit tests + Playwright
npm test -- --run
npx playwright test

# Watch mode (unit only)
npm test
```

**Output Example:**

```
 ✓ components/PlayerCard.test.tsx (3)
   ✓ renders player card correctly
   ✓ displays all required fields
   ✓ shows transfer suggestion when present

 ✓ components/StatusBadge.test.tsx (3)
   ✓ applies correct color for START
   ✓ applies correct color for RISK
   ✓ applies correct color for BENCH

 ✓ hooks/useImageUpload.test.ts (3)
   ✓ uploads and converts to base64
   ✓ rejects file over 20MB
   ✓ clears state

 ✓ utils/parseResponse.test.ts (2)
   ✓ parses JSON from markdown
   ✓ returns null on invalid JSON

Test Files  4 passed (4)
Tests      11 passed (11)
```

---

## Continuous Integration

### GitHub Actions

**File:** `.github/workflows/ci.yml`

Runs on every push to `main` and `develop` branches, and on pull requests.

**Jobs:**

1. **backend-lint** — Black + isort + pylint
2. **backend-test** — pytest (unit + integration, excludes E2E)
3. **frontend-lint** — TypeScript + ESLint
4. **frontend-test** — vitest
5. **docker-build** — Build Docker images

**Skipped Tests:**

- E2E tests (run locally only)

### Running Locally

```bash
# Simulate CI pipeline locally
cd backend && black . && isort . && pylint app/ --fail-under=7.0
cd backend && pytest tests/ --ignore=tests/e2e -v
cd frontend && npx tsc --noEmit && npm run lint
cd frontend && npm test -- --run
docker compose build
```

---

## Testing Best Practices

### Backend

1. **Always mock external APIs**

   ```python
   @patch('app.providers.anthropic.AnthropicProvider.generate_text')
   async def test_agent_with_mocked_llm(self, mock_generate):
       mock_generate.return_value = '{"key": "value"}'
       result = await agent_function()
   ```

2. **Use fixtures for common data**

   ```python
   @pytest.fixture
   def valid_squad_image():
       return base64.b64encode(open('tests/fixtures/squad.png', 'rb').read())
   ```

3. **Test error paths**
   ```python
   def test_image_validation_with_invalid_format():
       with pytest.raises(ValueError, match="format not supported"):
           validate_image(b'INVALID')
   ```

### Frontend

1. **Query by user-visible text**

   ```typescript
   expect(screen.getByText("Start Analysis")).toBeInTheDocument();
   ```

2. **Mock API calls**

   ```typescript
   vi.mock("../services/api", () => ({
     analyseSquad: vi.fn().mockResolvedValue(mockAnalysis),
   }));
   ```

3. **Test user interactions**
   ```typescript
   await userEvent.upload(input, file);
   await userEvent.click(screen.getByRole("button", { name: /analyze/i }));
   ```

---

## Debugging Tests

### Backend

```bash
# Verbose output
pytest tests/ -vv --tb=long

# Stop on first failure
pytest tests/ -x

# Run specific test
pytest tests/unit/test_utils.py::test_image_validation_rejects_gif -v

# Debug with pdb
pytest tests/ --pdb -s
```

### Frontend

```bash
# Debug UI tests
npm test -- --inspect-brk --ui

# Watch mode for specific file
npm test -- PlayerCard.test.tsx --watch

# Generate coverage report
npm test -- --coverage
```

---

## Test Coverage Reports

### Backend

```bash
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### Frontend

```bash
npm test -- --coverage
open coverage/index.html
```

---

## Troubleshooting Tests

| Issue                  | Solution                                                    |
| ---------------------- | ----------------------------------------------------------- |
| E2E tests fail locally | Install Playwright: `npx playwright install`                |
| API key tests fail     | Set `ANTHROPIC_API_KEY` or `GEMINI_API_KEY` env var         |
| Port already in use    | Kill process on port 8000: `lsof -ti:8000 \| xargs kill -9` |
| Image upload fails     | Ensure test image file exists: `tests/fixtures/squad.png`   |
| Type errors in tests   | Run `npm run typecheck` for full diagnostics                |

---

## Local vs CI/CD Differences

| Aspect             | Local                          | CI/CD                              |
| ------------------ | ------------------------------ | ---------------------------------- |
| E2E backend tests  | Run if API key set             | Skipped (`--ignore=tests/e2e`)     |
| E2E frontend tests | Playwright required            | Playwright pre-installed in Docker |
| Python version     | Any 3.11+                      | Pinned to 3.11                     |
| Node version       | Any 20+                        | Pinned to Node 20                  |
| Dependencies       | From requirements.txt          | Cached via GitHub Actions          |
| Linting            | Manual (`black`, `isort`, etc) | Automated on push                  |

---

## Next Steps

- [ ] Add performance benchmarks (agent latency)
- [ ] Implement mutation testing (verify test quality)
- [ ] Add visual regression tests (UI changes)
- [ ] Create test data factories for complex objects
