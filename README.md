# AI Document and Multimedia Q&A

## Overview
Full-stack application for uploading PDF, audio, and video files, asking grounded questions against uploaded content, generating summaries, extracting topic timestamps, and jumping playback to relevant media segments.

## Tech Stack
- Backend: FastAPI (Python)
- Frontend: React + Vite
- Database: PostgreSQL with pgvector
- Transcription: Whisper running locally
- LLM framework: LangChain + OpenAI API
- Caching: Redis
- Containerization: Docker + Docker Compose
- CI/CD: GitHub Actions

## Local Development

## Environment Setup

Create local `.env` files from the provided examples before running the project:

- `backend/.env` should define `DATABASE_URL`, `UPLOADS_DIR`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `WHISPER_MODEL`, `REDIS_URL`, `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXP_MINUTES`, `REFRESH_TOKEN_EXP_DAYS`, `RATE_LIMIT_PER_MINUTE`, `CHAT_CACHE_TTL_SECONDS`, and `UPLOAD_CACHE_TTL_SECONDS`.
- `frontend/.env` should define `VITE_API_BASE_URL`.
- For Docker Compose, also provide `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` if you want to override the defaults.
- Use a long random value for `JWT_SECRET_KEY`; do not reuse any shared password as the signing secret.
- Leave `OPENAI_API_KEY` blank only if you want fallback summarization and chat behavior.

### Backend
```powershell
cd backend
python -m pip install --upgrade pip
python -m pip install .[dev]
python -m pytest
uvicorn app.main:app --reload
```

### Frontend
```powershell
cd frontend
npm install
npm run lint
npm run build
npm run dev
```

## Docker Compose Setup

Use these commands to boot the full stack locally:

```powershell
docker compose up -d --build
docker compose ps
```

Expected container names:
- `indika-postgres`
- `indika-redis`
- `indika-backend`
- `indika-frontend`

Port mappings:
- PostgreSQL: `5432:5432`
- Redis: `6379:6379`
- FastAPI backend: `8000:8000`
- React frontend: `5173:5173`

Required environment variables:
- `OPENAI_API_KEY` for LLM-backed summarization and chat responses.
- Optional: `OPENAI_MODEL`, `WHISPER_MODEL`, `DATABASE_URL`, `UPLOADS_DIR`, `REDIS_URL`.

How to verify services after boot:
1. Check `docker compose ps` and ensure services are `running` or `healthy`.
2. Verify backend health at `http://localhost:8000/api/v1/health`.
3. Open the frontend at `http://localhost:5173`.
4. Confirm PostgreSQL is reachable on `localhost:5432` and Redis on `localhost:6379`.
5. Upload a file and confirm it appears in the UI and backend listing endpoint.

## API Documentation

### Health
- `GET /api/v1/health`

### Files
- `POST /api/v1/files/upload`
- `GET /api/v1/files`
- `GET /api/v1/files/{file_id}`
- `POST /api/v1/files/{file_id}/process`
- `GET /api/v1/files/{file_id}/summary`
- `GET /api/v1/files/{file_id}/transcript`

### Chat
- `POST /api/v1/chat/query`
- `GET /api/v1/chat/conversations/{conversation_id}`

### Timestamps / Media
- `POST /api/v1/timestamps/extract`
- `GET /api/v1/media/{file_id}/stream`

## Testing Instructions
Backend tests include upload, processing, retrieval, chatbot, timestamps, and service-level coverage.

```powershell
cd backend
python -m pytest
```

Frontend validation includes lint and production build.

```powershell
cd frontend
npm run lint
npm run build
```

## Run Instructions
1. Ensure Docker Desktop is installed or start backend/frontend services manually.
2. Set `OPENAI_API_KEY` if you want live summarization/chat responses from OpenAI.
3. Run `docker compose up -d --build` from the repository root.
4. Open the frontend at `http://localhost:5173`.
5. Use the upload panel to add PDFs, audio, or video files.
6. Process a file to generate summaries or transcripts.
7. Ask questions in the chatbot and use timestamp controls to jump playback for media.

## Requirement Traceability
See [docs/requirements-traceability.md](docs/requirements-traceability.md) for the full requirement-to-evidence matrix.

## Walkthrough
See [docs/walkthrough-script.md](docs/walkthrough-script.md) for the recording script.

## Validation Evidence
See [docs/final-coverage-evidence.md](docs/final-coverage-evidence.md) for final test and coverage evidence.

