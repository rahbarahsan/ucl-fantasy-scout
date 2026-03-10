# Troubleshooting Guide

## Common Issues & Solutions

---

## Backend Issues

### Backend Won't Start

**Error:** `Connection refused` or `Port 8000 already in use`

**Solution:**

```bash
# Check if port is in use
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001 --reload
```

---

### `.env` File Not Loading

**Error:** `Configuration error: ANTHROPIC_API_KEY not found`

**Solution:**

1. **Verify `.env` location:**

   ```bash
   # Should be in project root, not backend/
   ls -la .env
   ```

2. **Check path in config.py:**

   ```python
   # backend/app/config.py
   env_path = Path(__file__).parent.parent.parent / ".env"
   print(f"Loading from: {env_path}")
   ```

3. **File must be readable:**

   ```bash
   chmod 644 .env
   ```

4. **Verify format (no quotes):**

   ```env
   # ✅ Correct
   ANTHROPIC_API_KEY=sk-ant-...

   # ❌ Wrong
   ANTHROPIC_API_KEY="sk-ant-..."
   ```

---

### Image Upload Fails

**Error:** `Invalid image format` or `Image exceeds 20MB`

**Solution:**

1. **Check image format:**
   - Supported: PNG, JPEG, WebP, GIF
   - Not supported: TIFF, BMP, ICO

   ```bash
   file squad.png  # Returns: squad.png: PNG image data...
   ```

2. **Check image size:**

   ```bash
   du -h squad.png  # Returns: 500K    squad.png
   ```

3. **Validate Base64 encoding:**
   ```python
   import base64
   with open('squad.png', 'rb') as f:
       b64 = base64.b64encode(f.read()).decode()
       print(f"Length: {len(b64)}")
   ```

---

### API Rate Limiting / 429 Errors

**Error:** `HTTP 429 Too Many Requests`

**Solution:**

1. **Wait 60 seconds** — Rate limit is 10 req/min per IP

   ```bash
   sleep 60
   ```

2. **Check remaining requests:**

   ```bash
   curl -i http://localhost:8000/health | grep X-RateLimit
   ```

3. **Scale backend** for high traffic:
   ```bash
   docker compose up -d --scale backend=3
   ```

---

### Provider API Key Errors

**Error:** `Invalid API key` or `Authentication failed`

**Solution:**

1. **Verify API key format:**

   ```bash
   # Anthropic
   echo $ANTHROPIC_API_KEY | head -c 10  # Should start with: sk-ant-

   # Gemini
   echo $GEMINI_API_KEY | head -c 10     # Should start with: AIza or AIzaS...
   ```

2. **Test key validity:**

   ```bash
   # For Anthropic
   curl -X GET https://api.anthropic.com/v1/models \
     -H "x-api-key: $ANTHROPIC_API_KEY"

   # For Gemini
   curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"
   ```

3. **Check API quota:**
   - Anthropic: https://console.anthropic.com/account/usage
   - Google: https://console.cloud.google.com/billing

---

### JSON Parsing Errors

**Error:** `Failed to parse agent response`

**Solution:**

Backend automatically handles invalid JSON by:

1. Stripping markdown code fences (`json...`)
2. Returning empty object if parsing fails
3. Logging the raw response for debugging

To debug:

```python
# backend/app/agents/squad_parser.py
import logging
logger = logging.getLogger(__name__)

logger.debug(f"Raw response: {response}")
logger.debug(f"Parsed result: {parsed_result}")
```

---

### Encryption Errors

**Error:** `Decryption failed` or `Invalid encryption secret`

**Solution:**

1. **Verify ENCRYPTION_SECRET:**

   ```bash
   # Must be 32+ characters
   echo $ENCRYPTION_SECRET | wc -c  # Should show >= 33 (includes newline)
   ```

2. **Check consistency:**
   - Frontend and backend must use same secret for key decryption
   - If you change it, all previously encrypted keys are invalid

3. **Regenerate secret:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

---

### Database Connection Errors (if using DB)

**Error:** `Cannot connect to database`

**Solution:**

```bash
# Verify postgres is running
docker compose ps postgres

# Check connection
psql -h localhost -U postgres -d ucl_fantasy -c "SELECT 1"

# View logs
docker compose logs postgres
```

---

## Frontend Issues

### Frontend Dev Server Won't Start

**Error:** `Port 5173 already in use` or `EADDRINUSE`

**Solution:**

```bash
# Kill existing process
lsof -i :5173 | tail -1 | awk '{print $2}' | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

---

### API Calls Fail / CORS Errors

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**

1. **Verify backend is running:**

   ```bash
   curl http://localhost:8000/health
   ```

2. **Check VITE_API_BASE:**

   ```javascript
   // src/services/api.ts
   console.log("API Base:", API_BASE); // Should be http://localhost:8000
   ```

3. **Verify proxy in vite.config.ts:**

   ```typescript
   server: {
     proxy: {
       '/api': {
         target: 'http://localhost:8000',
         changeOrigin: true
       }
     }
   }
   ```

4. **Backend CORS middleware:**
   ```python
   # backend/app/api/middleware.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=['http://localhost:5173'],
       allow_methods=['*'],
       allow_headers=['*']
   )
   ```

---

### TypeScript Errors

**Error:** `Type 'X' is not assignable to type 'Y'`

**Solution:**

1. **Run type check:**

   ```bash
   npm run typecheck
   ```

2. **Check your types are correct:**

   ```typescript
   // ❌ Wrong - Player is not a string
   const player: Player = "Harry Kane";

   // ✅ Correct
   const player: Player = {
     name: "Harry Kane",
     position: "FWD",
     verdict: "START",
     confidence: 0.95,
     reasoning: "...",
   };
   ```

3. **Import types correctly:**

   ```typescript
   // ✅ Correct
   import type { Player } from "../types";

   // ❌ Wrong (imports value, not type)
   import { Player } from "../types";
   ```

4. **Update tsconfig.json if needed:**
   ```bash
   npm run typecheck -- --noEmit --strict
   ```

---

### ESLint/Prettier Errors

**Error:** `Expected indentation of 2 spaces`

**Solution:**

```bash
# Auto-fix all files
npm run format

# Or manually with prettier
npx prettier --write src/
```

---

### Image Upload Not Working

**Error:** File selection doesn't trigger upload, or base64 is empty

**Solution:**

1. **Check file input is correct:**

   ```typescript
   // src/components/SquadUploader.tsx
   const input = document.getElementById("file-input") as HTMLInputElement;
   console.log(input.files);
   ```

2. **Verify FileReader API:**

   ```typescript
   const reader = new FileReader();
   reader.onload = (e) => {
     console.log("Result:", e.target?.result); // Should be base64 string
   };
   ```

3. **Check file size:**
   ```typescript
   console.log("File size:", file.size / 1024 / 1024, "MB"); // Should be < 20
   ```

---

### State Not Updating

**Error:** `Loading indicator stuck` or `Results don't show`

**Solution:**

1. **Check React state hooks:**

   ```typescript
   const [loading, setLoading] = useState(false);

   // Make sure you're setting state correctly
   await new Promise((r) => setTimeout(r, 0)); // Allow React to update
   ```

2. **Verify useEffect dependencies:**

   ```typescript
   useEffect(() => {
     // Will run every render if deps are missing!
     fetchData();
   }, []); // ✅ Always include deps array
   ```

3. **Check Context providers:**
   ```typescript
   // Make sure component is inside App wrapper
   <AppProvider>
     <YourComponent />  {/* Can access context */}
   </AppProvider>
   ```

---

## Docker Issues

### Docker Build Fails

**Error:** `Cannot locate Dockerfile` or `Build context error`

**Solution:**

```bash
# Verify Dockerfile exists
ls -la backend/Dockerfile frontend/Dockerfile

# Build specific service
docker compose build backend --no-cache

# Verbose output
docker compose build backend --progress=plain
```

---

### Container Exits Immediately

**Error:** `docker compose up` exits with no output

**Solution:**

```bash
# Check logs
docker compose logs backend

# Run container interactively to see startup
docker compose run backend bash

# Inside container, try manual command
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### Network Connectivity Between Containers

**Error:** `Cannot reach backend from frontend container`

**Solution:**

```bash
# Verify network exists
docker network ls

# Check container IPs
docker compose exec backend hostname -I

# Test connectivity
docker compose exec frontend ping backend

# Check DNS
docker compose exec frontend nslookup backend
```

---

### Volume Mounting Issues

**Error:** `Volume mount not found` or `Permission denied`

**Solution:**

```bash
# Check volumes
docker volume ls

# Verify mount path
docker compose exec backend ls -la /app

# Fix permissions
docker compose exec backend chmod -R 755 /app
```

---

## Git & Deployment Issues

### Git Push Fails

**Error:** `Permission denied` or `repository not found`

**Solution:**

```bash
# Check SSH key
cat ~/.ssh/id_rsa.pub

# Or use HTTPS with token
git remote set-url origin https://github.com/rahbarahsan/ucl-fantasy-scout.git

# Authenticate
git config credential.helper store
git push origin main
```

---

### GitHub Actions Fails

**Error:** CI/CD pipeline fails on main branch

**Solution:**

1. **Check logs:**
   - Navigate to https://github.com/rahbarahsan/ucl-fantasy-scout/actions
   - Click failed workflow
   - Expand error log

2. **Common causes:**
   - Missing environment secrets
   - Python version mismatch
   - Node version mismatch
   - Linting failures

3. **Fix locally first:**
   ```bash
   # Run same checks locally
   black --check .
   npm run lint
   pytest tests/ --ignore=tests/e2e
   ```

---

## Performance Issues

### Backend Response Slow

**Symptoms:** Analysis takes >30 seconds

**Solutions:**

1. **Check provider API performance:**

   ```bash
   time curl "https://api.anthropic.com/v1/messages" \
     -H "x-api-key: $ANTHROPIC_API_KEY"
   ```

2. **Analyze agent pipeline:**

   ```python
   # backend/app/utils/logger.py
   # Add timing logs
   start = time.time()
   result = await agent_function()
   elapsed = time.time() - start
   logger.info(f"Agent took {elapsed:.2f}s")
   ```

3. **Cache results:**
   - Don't re-parse same image
   - Store fixture data
   - Use Redis for hot data

---

### Frontend Slow Load

**Symptoms:** Page takes >5 seconds to load

**Solutions:**

1. **Check bundle size:**

   ```bash
   npm run build
   npm run analyze
   ```

2. **Enable compression:**

   ```bash
   npm run build -- --minify=terser
   ```

3. **Use lazy loading:**
   ```typescript
   const ResultsPanel = lazy(() => import("./ResultsPanel"));
   ```

---

## Data Loss / Corruption

### Lost Analysis Results

**Solution:** Currently results are not persisted. Implement database:

```python
# backend/app/models.py
from sqlalchemy import Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analyses"
    id = Column(String, primary_key=True)
    matchday = Column(Integer)
    results = Column(JSON)
```

---

### Corrupted Files in Docker

**Solution:**

```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## Debugging Tools

### Backend Debugging

**Add to code:**

```python
import pdb; pdb.set_trace()
```

**Run with debugger:**

```bash
python -m pdb -m pytest tests/unit/test_utils.py
```

---

### Frontend Debugging

**Browser DevTools:**

- Press `F12` or `Ctrl+Shift+I`
- Console tab for errors
- Network tab for API calls
- Storage tab for localStorage

**Debug in VSCode:**

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "chrome",
      "request": "launch",
      "name": "Launch Chrome",
      "url": "http://localhost:5173",
      "webRoot": "${workspaceFolder}/frontend"
    }
  ]
}
```

---

## Getting Help

1. **Check logs:**

   ```bash
   # Backend
   docker compose logs backend

   # Frontend (browser console)
   F12 → Console
   ```

2. **Search existing issues:**
   https://github.com/rahbarahsan/ucl-fantasy-scout/issues

3. **Create new issue with:**
   - Error message (full trace)
   - Steps to reproduce
   - Environment (OS, Python/Node version)
   - Logs and screenshots

---

## Reporting Bugs

Include in issue report:

- [ ] Error message
- [ ] Steps to reproduce
- [ ] Expected behavior
- [ ] Actual behavior
- [ ] Logs/screenshots
- [ ] OS and version info
- [ ] Python/Node version
- [ ] Browser (if frontend)
