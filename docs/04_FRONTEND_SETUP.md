# Frontend Setup & Architecture

## Overview

The frontend is a **React + Vite** single-page application (SPA) with TypeScript, Tailwind CSS, and PWA support. It provides two main interfaces:

1. **Squad Analysis** — Upload screenshot, receive AI-powered verdicts
2. **Ad-Hoc Research** — Chat-style interface for UCL Fantasy questions

---

## Tech Stack

- **Runtime:** Node.js 20+
- **Framework:** React 18.3.1
- **Build Tool:** Vite 6.0.5
- **Language:** TypeScript 5.7.2
- **Styling:** Tailwind CSS 3.4.17
- **PWA:** vite-plugin-pwa
- **HTTP Client:** axios
- **State Management:** React hooks + Context (no Redux needed)
- **Testing:** Vitest 2.1.9, React Testing Library, Playwright (E2E)
- **Linting:** ESLint, Prettier, npm audit

---

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── SquadUploader.tsx        # Image upload component
│   │   ├── PlayerCard.tsx           # Individual player verdict card
│   │   ├── ResultsSummary.tsx       # Summary of all verdicts
│   │   ├── StatusBadge.tsx          # Verdict status badge (START/RISK/BENCH)
│   │   ├── AdHocChat.tsx            # Research Q&A interface
│   │   ├── SettingsPanel.tsx        # API key configuration
│   │   └── Layout.tsx               # App layout wrapper
│   │
│   ├── hooks/
│   │   ├── useImageUpload.ts        # Handle image upload & validation
│   │   ├── useAnalysis.ts           # Manage analysis state machine
│   │   └── useAdHocResearch.ts      # Handle research requests
│   │
│   ├── services/
│   │   ├── api.ts                   # HTTP client & endpoints
│   │   └── storage.ts               # LocalStorage helpers
│   │
│   ├── utils/
│   │   ├── imageToBase64.ts         # File to Base64 conversion
│   │   ├── encryptKey.ts            # XOR encryption for API keys
│   │   ├── parseResponse.ts         # Parse AI response JSON
│   │   └── constants.ts             # App constants
│   │
│   ├── types/
│   │   ├── index.ts                 # TypeScript interfaces
│   │   └── api.ts                   # API types
│   │
│   ├── constants/
│   │   └── index.ts                 # Config constants (positions, providers, etc)
│   │
│   ├── App.tsx                      # Root component (tab navigation)
│   ├── App.css                      # Global styles
│   ├── main.tsx                     # Vite entry point
│   └── vite-env.d.ts                # Vite type definitions
│
├── tests/
│   ├── components/
│   │   ├── PlayerCard.test.tsx
│   │   └── StatusBadge.test.tsx
│   ├── hooks/
│   │   └── useImageUpload.test.ts
│   ├── utils/
│   │   └── parseResponse.test.ts
│   └── e2e/
│       └── examples.spec.ts         # Playwright E2E tests
│
├── public/
│   ├── manifest.webmanifest         # PWA manifest
│   └── icons/                       # App icons
│
├── Dockerfile
├── vite.config.ts
├── tsconfig.json
├── eslint.config.js
├── prettier.config.js
└── package.json
```

---

## Installation & Setup

### Prerequisites

- Node.js 20+
- npm or yarn

### Local Development

1. **Clone & navigate:**
   ```bash
   git clone https://github.com/rahbarahsan/ucl-fantasy-scout.git
   cd ucl-fantasy-scout/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run dev server:**
   ```bash
   npm run dev
   ```

   App opens at `http://localhost:5173`
   - Hot module reload enabled
   - Frontend automatically proxies to `http://localhost:8000` for backend

4. **Build for production:**
   ```bash
   npm run build
   ```

   Output in `dist/` — ready for deployment

---

## Configuration

### API Endpoint

**File:** `src/services/api.ts`

Backend URL detected from environment:

```typescript
const API_BASE = process.env.VITE_API_BASE || 'http://localhost:8000'
```

**For Docker:** Set `VITE_API_BASE=http://backend:8000` in `.env`

### API Key Management

API keys are stored locally and encrypted with **XOR cipher** before sending to backend:

```typescript
// src/utils/encryptKey.ts
export function encryptKey(key: string, secret: string): string {
  // XOR-based encryption
}
```

**Security notes:**
- Keys stored in browser `SessionStorage` (cleared on tab close)
- Never logged or sent to third parties
- Backend does server-side AES-256 encryption

---

## Core Components

### 1. Squad Uploader

**File:** `src/components/SquadUploader.tsx`

Input component for squad screenshot upload.

**Features:**
- Drag-and-drop support
- File preview
- Validation (PNG/JPEG/WebP, max 20MB)
- Loading state during upload

**Props:**
```typescript
interface SquadUploaderProps {
  onImageSelected: (base64: string) => void;
  isLoading?: boolean;
  error?: string;
}
```

---

### 2. Player Card

**File:** `src/components/PlayerCard.tsx`

Displays individual player analysis result.

```typescript
interface PlayerCardProps {
  player: {
    name: string;
    position: Position;
    opponent: string;
    verdict: "START" | "RISK" | "BENCH";
    confidence: number;
    reasoning: string;
    suggested_transfer?: string;
  };
}
```

---

### 3. Status Badge

**File:** `src/components/StatusBadge.tsx`

Visual badge for verdict status.

```typescript
interface StatusBadgeProps {
  status: "START" | "RISK" | "BENCH";
  confidence?: number;
}
```

**Colors:**
- `START` → Green (#10B981)
- `RISK` → Yellow (#F59E0B)
- `BENCH` → Red (#EF4444)

---

### 4. AdHoc Chat

**File:** `src/components/AdHocChat.tsx`

Research question interface.

**Features:**
- Text input for questions
- Message history
- Source links
- Loading state

---

### 5. Settings Panel

**File:** `src/components/SettingsPanel.tsx`

Manage API keys and app settings.

**Features:**
- Provider selection (Anthropic / Gemini)
- API key input (encrypted storage)
- Log level selector
- Clear all data button

---

## Custom Hooks

### `useImageUpload()`

**File:** `src/hooks/useImageUpload.ts`

Manages image upload and validation.

```typescript
const {
  imageBase64,
  fileName,
  isLoading,
  error,
  uploadImage,
  clear
} = useImageUpload();
```

**Logic:**
- File to Base64 conversion
- Size validation (max 20MB)
- Format validation (PNG/JPEG/WebP/GIF)
- Error handling

---

### `useAnalysis()`

**File:** `src/hooks/useAnalysis.ts`

State machine for analysis flow.

```typescript
const {
  state,           // 'idle' | 'loading' | 'awaitingMatchday' | 'complete' | 'error'
  analysis,
  error,
  submitImage,     // (base64, provider) => Promise<void>
  confirmMatchday, // (matchday) => Promise<void>
  reset
} = useAnalysis();
```

**States:**
- `idle` → Ready for upload
- `loading` → API call in progress
- `awaitingMatchday` → Waiting for user confirmation
- `complete` → Results ready
- `error` → Error occurred

---

### `useAdHocResearch()`

**File:** `src/hooks/useAdHocResearch.ts`

Handle research questions.

```typescript
const {
  messages,
  isLoading,
  error,
  askQuestion,
  clearMessages
} = useAdHocResearch();
```

---

## API Service

**File:** `src/services/api.ts`

HTTP client wrapper with Axios.

```typescript
export async function analyseSquad(
  imagBase64: string,
  provider: "anthropic" | "gemini"
): Promise<AnalysisResult>

export async function askResearch(
  question: string,
  provider: "anthropic" | "gemini"
): Promise<ResearchResponse>

export async function checkHealth(): Promise<{ status: string }>
```

**Features:**
- Automatic error handling
- Request timeout (30s)
- Retry logic (3 attempts)

---

## TypeScript Types

**File:** `src/types/index.ts`

```typescript
export type Position = "DEF" | "MID" | "FWD";
export type Verdict = "START" | "RISK" | "BENCH";
export type ProviderKey = "anthropic" | "gemini";
export type Confidence = "HIGH" | "MEDIUM" | "LOW";

export interface Player {
  name: string;
  position: Position;
  opponent: string;
  verdict: Verdict;
  confidence: number;
  reasoning: string;
  suggested_transfer?: string;
}

export interface AnalysisResult {
  matchday: number;
  analysis_quality: Confidence;
  players: Player[];
  summary: string;
}
```

---

## PWA Configuration

**File:** `vite.config.ts`

Configured with `vite-plugin-pwa`:

```typescript
import { VitePWA } from 'vite-plugin-pwa/react'

export default {
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'UCL Fantasy Scout',
        icons: [...]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html}']
      }
    })
  ]
}
```

**Features:**
- Offline fallback shell
- Service Worker caching
- Installable on mobile
- Auto-update on new releases

---

## Testing

### Unit Tests

```bash
cd frontend
npm install
npm test -- --run
```

**Coverage:**
- `PlayerCard.test.tsx` — Component rendering & props
- `StatusBadge.test.tsx` — Badge status & colors
- `useImageUpload.test.ts` — Upload logic & validation
- `parseResponse.test.ts` — JSON parsing utilities

**Run in watch mode:**
```bash
npm test
```

---

### E2E Tests (Playwright)

```bash
npx playwright install
npx playwright test
```

**Coverage:**
- Full user flow: Upload → Matchday confirmation → Results
- Error states: Invalid images, network errors
- Settings: API key configuration

---

## Build & Deployment

### Development

```bash
npm run dev
```

### Build Production

```bash
npm run build   # Creates dist/
npm run preview # Preview optimized build
```

### Docker

```bash
# Build
docker build -t ucl-fantasy-scout-frontend:latest .

# Run
docker run -p 3000:80 \
  -e VITE_API_BASE=http://backend:8000 \
  ucl-fantasy-scout-frontend:latest
```

### Docker Compose

```bash
docker compose up frontend
```

---

## Linting & Formatting

### ESLint

```bash
npm run lint          # Check
npm run lint -- --fix # Auto-fix
```

### Prettier

```bash
npm run format        # Format all files
```

### Type Checking

```bash
npm run typecheck
```

### Audit

```bash
npm audit
npm audit fix
```

---

## Performance Optimization

### Code Splitting

Vite automatically code-splits route components.

### Image Optimization

Squad screenshots are base64-encoded client-side to reduce network overhead.

### Caching

Service Worker caches static assets for offline access.

### Bundle Analysis

```bash
npm run analyze  # Generates bundle size report
```

---

## Environment Variables

**File:** `.env` (frontend root)

```env
VITE_API_BASE=http://localhost:8000
VITE_LOG_LEVEL=debug
```

---

## Troubleshooting

### Common Issues

1. **CORS errors when calling backend**
   - Ensure backend is running: `uvicorn app.main:app --reload`
   - Check `VITE_API_BASE` is correct
   - Verify backend has CORS middleware enabled

2. **Image upload fails**
   - Check file is PNG/JPEG/WebP (not TIFF, BMP, etc)
   - Ensure file is under 20MB
   - Look for browser console errors

3. **TypeScript errors**
   - Run `npm run typecheck` for full diagnostics
   - Clear `.eslintcache`: `rm .eslintcache`

4. **PWA not installing**
   - Must be HTTPS (or localhost for testing)
   - Manifest.webmanifest must be served with correct MIME type
   - Service Worker must be registered

---

## Next Steps

- [ ] Add dark mode support
- [ ] Implement squad history (requires backend persistence)
- [ ] Add player search/filter in results
- [ ] Multi-language support (i18n)
- [ ] Mobile-optimized layout
