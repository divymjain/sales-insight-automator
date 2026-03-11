# 📊 Sales Insight Automator — Rabbitt AI

> Upload sales data → AI generates executive briefing → Email delivered in seconds.

[![CI](https://github.com/your-org/sales-insight-automator/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/sales-insight-automator/actions)

---

## 🔗 Live Deployment

| Service | URL |
|---|---|
| **Frontend (SPA)** | `https://sales-insight.vercel.app` |
| **Backend API** | `https://sales-insight-api.onrender.com` |
| **Swagger UI** | `https://sales-insight-api.onrender.com/docs` |
| **ReDoc** | `https://sales-insight-api.onrender.com/redoc` |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────┐        ┌──────────────────────────────────┐
│  React SPA (Vite)       │  POST  │  FastAPI Backend                 │
│  - File drag-and-drop   │───────▶│  /api/v1/analyze                 │
│  - Email input          │        │                                  │
│  - Real-time progress   │        │  1. Validate file + rate limit   │
│  - Success/error states │        │  2. Parse CSV/XLSX (pandas)      │
└─────────────────────────┘        │  3. Build stats summary          │
                                   │  4. Call Gemini/Groq LLM         │
                                   │  5. Send HTML email              │
                                   └──────────┬───────────────────────┘
                                              │
                              ┌───────────────┴────────────────┐
                              │                                │
                    ┌─────────▼──────┐             ┌──────────▼───────┐
                    │  Gemini Flash  │             │  SendGrid/SMTP   │
                    │  (LLM)         │             │  (Email)         │
                    └────────────────┘             └──────────────────┘
```

---

## 🚀 Quick Start with Docker Compose

### Prerequisites
- Docker ≥ 24 and Docker Compose ≥ 2.24
- API keys for your chosen LLM and email provider

### 1. Clone and configure

```bash
git clone https://github.com/your-org/sales-insight-automator.git
cd sales-insight-automator

cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
```

### 2. Spin up the full stack

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

### 3. Test with the sample file

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -F "file=@sales_q1_2026.csv" \
  -F "recipient_email=you@example.com"
```

### Stop and clean up

```bash
docker-compose down -v
```

---

## 🔒 Security Implementation

### 1. API Key Authentication
Every request to `/api/v1/*` must include an `X-API-Key` header. The key is validated using `secrets.compare_digest()` to prevent timing attacks.

```
X-API-Key: your-strong-api-key-here
```

### 2. Rate Limiting
`slowapi` enforces **10 requests/minute per IP** on the `/analyze` endpoint. Requests exceeding this return `HTTP 429`.

### 3. File Validation (Defense-in-depth)
- **Extension check**: Only `.csv`, `.xlsx`, `.xls` accepted
- **Size limit**: Files above 10 MB are rejected (HTTP 413)
- **Empty file guard**: Zero-byte uploads rejected
- **Content parsing**: Files that can't be parsed by pandas return HTTP 422

### 4. Input Sanitisation
- Email addresses are validated via regex before processing
- All data is processed in memory — no files written to disk

### 5. Non-root Container
The production Docker image runs as `appuser` (non-root), reducing the blast radius of any container escape.

### 6. Security Headers (Frontend)
The nginx config sets `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, `Referrer-Policy`, and a `Content-Security-Policy`.

### 7. CORS Policy
The backend's CORS middleware only allows requests from explicitly configured origins (`ALLOWED_ORIGINS` env var).

---

## 🌿 Environment Variables

See [`backend/.env.example`](backend/.env.example) for the full reference. Key variables:

| Variable | Description |
|---|---|
| `INTERNAL_API_KEY` | API key clients must send in `X-API-Key` header |
| `LLM_PROVIDER` | `gemini` or `groq` |
| `GEMINI_API_KEY` | Google AI Studio key |
| `GROQ_API_KEY` | Groq console key |
| `EMAIL_PROVIDER` | `smtp` or `sendgrid` |
| `SMTP_USER` / `SMTP_PASSWORD` | SMTP credentials (use Gmail App Password) |
| `SENDGRID_API_KEY` | SendGrid API key |
| `RATE_LIMIT_PER_MINUTE` | Requests per IP per minute (default: 10) |
| `MAX_FILE_SIZE_MB` | Upload limit in MB (default: 10) |

---

## 🧱 Project Structure

```
sales-insight-automator/
├── backend/
│   ├── app/
│   │   ├── api/routes.py          # FastAPI route handlers
│   │   ├── core/
│   │   │   ├── config.py          # Pydantic settings
│   │   │   └── security.py        # API key auth + file validation
│   │   ├── services/
│   │   │   ├── data_parser.py     # CSV/XLSX → stats dict
│   │   │   ├── ai_service.py      # Gemini/Groq integration
│   │   │   └── email_service.py   # SMTP/SendGrid delivery
│   │   ├── models/schemas.py      # Pydantic response models
│   │   └── main.py                # App factory + middleware
│   ├── requirements.txt
│   ├── Dockerfile                 # Multi-stage, non-root
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # SPA with upload/status/success flows
│   │   ├── App.css                # Design system + component styles
│   │   └── main.jsx
│   ├── Dockerfile                 # Multi-stage → nginx
│   ├── nginx.conf                 # SPA routing + security headers
│   └── package.json
├── .github/
│   └── workflows/ci.yml           # PR lint + build + docker validate
├── docker-compose.yml
├── sales_q1_2026.csv              # Sample test data
└── README.md
```

---

## ⚙️ CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) triggers on **every PR to `main`**:

| Job | What it does |
|---|---|
| `backend-lint-test` | Ruff linting + mypy type check |
| `backend-docker-build` | Full Docker image build (with layer caching) |
| `frontend-lint-build` | ESLint + `vite build` |
| `frontend-docker-build` | Full Docker image build |
| `ci-summary` | Final pass/fail report |

Merging to `main` can be extended to trigger deployment via Render/Vercel deploy hooks.

---

## 🚢 Deployment

### Backend → Render
1. Create a **Web Service**, connect your GitHub repo
2. Set **Root Directory** to `backend`
3. Set **Docker** as the runtime (uses the `Dockerfile` automatically)
4. Add environment variables in the Render dashboard

### Frontend → Vercel
1. Import the repo, set **Root Directory** to `frontend`
2. Framework: **Vite**
3. Set env vars: `VITE_API_URL`, `VITE_API_KEY`

---

## 🧪 Manually Testing the API

With the stack running:

```bash
# Health check
curl http://localhost:8000/health

# Service configuration status
curl http://localhost:8000/api/v1/status

# Full analysis (replace email)
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "X-API-Key: dev-api-key-change-in-production" \
  -F "file=@sales_q1_2026.csv" \
  -F "recipient_email=you@example.com"
```

Or open the **Swagger UI** at http://localhost:8000/docs for an interactive experience.

---

*Built by: [Your Name] · Rabbitt AI Sprint · March 2026*
