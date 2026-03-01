# API Reference

## Base URL

```
http://localhost:8000        # Local development
http://your-domain.com       # Production
```

All endpoints require the `Content-Type: application/json` header unless otherwise specified.

---

## Authentication

### API Key Authentication

Pass your encrypted API key via the `X-API-Key` header:

```bash
curl -X POST http://localhost:8000/api/analyse \
  -H "X-API-Key: encrypted-key-here" \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "..."}'
```

**How it works:**
1. Frontend encrypts the API key client-side using XOR cipher
2. Backend receives encrypted key and decrypts it server-side (AES-256)
3. Decrypted key is used for the current request only
4. Original key is never stored server-side

**API Key Source:**
- From `X-API-Key` header (if provided)
- Falls back to `ANTHROPIC_API_KEY` or `GEMINI_API_KEY` from `.env`

---

## Rate Limiting

- **Limit:** 10 requests per minute per IP address
- **Headers:**
  - `X-RateLimit-Limit: 10` — Max requests
  - `X-RateLimit-Remaining: 5` — Requests remaining
  - `X-RateLimit-Reset: 1234567890` — Unix timestamp when reset

**HTTP 429 (Too Many Requests):**
```json
{
  "detail": "Rate limit exceeded. Try again in 60s.",
  "retry_after": 60
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "ERROR_TYPE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

| HTTP | Error Code | Description |
|------|-----------|-------------|
| 400 | `INVALID_IMAGE` | Image format not supported or corrupted |
| 400 | `IMAGE_TOO_LARGE` | Image exceeds 20MB limit |
| 401 | `UNAUTHORIZED` | Missing or invalid API key |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `PROVIDER_ERROR` | AI provider API error |
| 500 | `INTERNAL_ERROR` | Server error |

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the backend is running.

**Response:** `200 OK`
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Analyze Squad

**POST** `/api/analyse`

Submit a squad screenshot for analysis through the 8-agent pipeline.

**Request:**

```json
{
  "image_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "provider": "anthropic"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image_base64` | string | Yes | Base64-encoded image (PNG/JPEG/WebP/GIF) |
| `provider` | string | No | `"anthropic"` or `"gemini"` (default: `anthropic`) |

**Response:** `200 OK`

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
      "reasoning": "Strong fixture against Barcelona. Exceptional form with 5 goals in last 4 games. Low rotation risk.",
      "suggested_transfer": null
    },
    {
      "name": "Rodri",
      "position": "MID",
      "opponent": "Real Madrid",
      "verdict": "RISK",
      "confidence": 0.72,
      "reasoning": "Difficult fixture. Has played 180+ minutes recently - rotation likely.",
      "suggested_transfer": "Foden"
    },
    {
      "name": "ter Stegen",
      "position": "DEF",
      "opponent": "Manchester City",
      "verdict": "BENCH",
      "confidence": 0.88,
      "reasoning": "Very difficult fixture. Barcelona 0-4 down in aggregate - likely to rotate.",
      "suggested_transfer": "Lunin"
    }
  ],
  "summary": "Strong squad for MD6. Kane is essential. Consider benching ter Stegen and rotating Rodri. Look at alternative midfielders for depth."
}
```

**Player Object:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Player name |
| `position` | enum | `"DEF"`, `"MID"`, `"FWD"` |
| `opponent` | string | Upcoming opponent |
| `verdict` | enum | `"START"`, `"RISK"`, `"BENCH"` |
| `confidence` | float | 0.0-1.0 confidence score |
| `reasoning` | string | Explanation for the verdict |
| `suggested_transfer` | string \| null | Recommended replacement player |

**Error Responses:**

- `400` — Invalid image or format
- `401` — Unauthorized (missing API key)
- `429` — Rate limited
- `500` — Provider error (e.g., API quota exceeded)

**Example:**
```bash
curl -X POST http://localhost:8000/api/analyse \
  -H "X-API-Key: your-encrypted-key" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/png;base64,...",
    "provider": "anthropic"
  }'
```

---

### 3. Ad-Hoc Research

**POST** `/api/research`

Ask a question about UCL Fantasy and get a sourced answer.

**Request:**

```json
{
  "question": "Which teams are resting players in the Group Stage?",
  "provider": "anthropic"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `question` | string | Yes | Your UCL Fantasy question (1-500 chars) |
| `provider` | string | No | `"anthropic"` or `"gemini"` (default: `anthropic`) |

**Response:** `200 OK`

```json
{
  "answer": "Based on recent reports and team schedules:\n\n- **Manchester City**: Likely to rotate in group matches, focusing on the Premier League\n- **Bayern Munich**: May rest key players in early knockouts\n- **Real Madrid**: Historically maintains full strength in UCL\n\nWatch for official team sheets 24 hours before kickoff.",
  "sources": [
    {
      "title": "Manchester City to rotate squad for UCL group",
      "url": "https://www.espn.com/...",
      "snippet": "City manager confirmed plans to rest players in early group matches..."
    },
    {
      "title": "Bayern Munich resting policy for 2024-25 season",
      "url": "https://www.goal.com/...",
      "snippet": "Bayern Munich will prioritize rotation in the group stage to manage player fatigue..."
    }
  ],
  "confidence": "MEDIUM"
}
```

**Response Object:**

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Direct answer to the question |
| `sources` | array | List of source articles |
| `confidence` | enum | `"HIGH"`, `"MEDIUM"`, `"LOW"` |

**Source Object:**

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Article title |
| `url` | string | Link to source |
| `snippet` | string | Relevant excerpt |

**Error Responses:**

- `400` — Invalid question format
- `401` — Unauthorized
- `429` — Rate limited
- `500` — Provider error

**Example:**
```bash
curl -X POST http://localhost:8000/api/research \
  -H "X-API-Key: your-encrypted-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Is Haaland fit for the next match?",
    "provider": "gemini"
  }'
```

---

## Request/Response Headers

### Common Headers

| Header | Value | Required | Description |
|--------|-------|----------|-------------|
| `Content-Type` | `application/json` | Yes | Always JSON |
| `User-Agent` | Any | No | Identifies your client |
| `X-API-Key` | Encrypted key | No | API authentication |

### Response Headers

| Header | Value | Example |
|--------|-------|---------|
| `X-RateLimit-Limit` | Max requests/min | `10` |
| `X-RateLimit-Remaining` | Requests left | `5` |
| `X-RateLimit-Reset` | Unix timestamp | `1705329000` |
| `Content-Type` | `application/json` | Always set |

---

## Response Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input (image too large, invalid format) |
| 401 | Unauthorized | Missing or invalid API key |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Backend error (provider API down, etc) |

---

## Usage Examples

### Python (requests)

```python
import requests
import base64

with open('squad_screenshot.png', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

response = requests.post(
    'http://localhost:8000/api/analyse',
    headers={
        'X-API-Key': 'your-encrypted-key',
        'Content-Type': 'application/json'
    },
    json={
        'image_base64': f'data:image/png;base64,{image_data}',
        'provider': 'anthropic'
    }
)

analysis = response.json()
print(f"Matchday: {analysis['matchday']}")
for player in analysis['players']:
    print(f"{player['name']}: {player['verdict']} ({player['confidence']:.0%})")
```

### JavaScript (fetch)

```javascript
const imageFile = document.getElementById('upload').files[0];
const reader = new FileReader();

reader.onload = async (e) => {
  const imageBase64 = e.target.result;
  
  const response = await fetch('http://localhost:8000/api/analyse', {
    method: 'POST',
    headers: {
      'X-API-Key': 'your-encrypted-key',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      image_base64: imageBase64,
      provider: 'anthropic'
    })
  });
  
  const analysis = await response.json();
  console.log(`Matchday ${analysis.matchday}:`, analysis.players);
};

reader.readAsDataURL(imageFile);
```

### cURL

```bash
# Squad analysis
curl -X POST http://localhost:8000/api/analyse \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d @- << EOF
{
  "image_base64": "data:image/png;base64,$(base64 < squad.png)",
  "provider": "anthropic"
}
EOF

# Ad-hoc research
curl -X POST http://localhost:8000/api/research \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Who are the top scorers in MD6?"
  }'
```

---

## Rate Limiting Details

**Policy:** 10 requests per minute per IP address

**Behavior:**
- Requests 1-10 succeed
- Request 11+ returns 429 with `Retry-After: 60`
- Counter resets every minute

**Headers:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1705329060
```

---

## Pagination & Filtering

Currently, no endpoints support pagination. All responses are single objects or arrays.

---

## Webhooks

Not yet implemented. Consider for V2 if you need async analysis delivery.

---

## Changelog

### v1.0.0 (Current)
- `/health` — Health check
- `/api/analyse` — Squad analysis
- `/api/research` — Ad-hoc research
- Rate limiting (10 req/min)
- API key authentication

### Future (v1.1+)
- Async analysis jobs
- Squad history persistence
- Webhook deliveries
- Advanced filtering & search
