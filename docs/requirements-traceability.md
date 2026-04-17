# Requirement Traceability

## Core Requirements

| Requirement ID | Status | Evidence |
| --- | --- | --- |
| C1 | Verified | Upload flow implemented in [backend/app/api/v1/files.py](../backend/app/api/v1/files.py) and tested in [backend/tests/test_files_api.py](../backend/tests/test_files_api.py). |
| C2 | Verified | Chat query endpoint and conversation history in [backend/app/api/v1/chat.py](../backend/app/api/v1/chat.py) with UI in [frontend/src/components/ChatPanel.jsx](../frontend/src/components/ChatPanel.jsx). |
| C3 | Verified | Processing and summary endpoints in [backend/app/api/v1/files.py](../backend/app/api/v1/files.py) and summary UI in [frontend/src/components/SummaryPanel.jsx](../frontend/src/components/SummaryPanel.jsx). |
| C4 | Verified | Timestamp extraction endpoint in [backend/app/api/v1/timestamps.py](../backend/app/api/v1/timestamps.py) and UI in [frontend/src/components/TimestampPanel.jsx](../frontend/src/components/TimestampPanel.jsx). |
| C5 | Verified | Media stream endpoint and playback jump UI in [backend/app/api/v1/timestamps.py](../backend/app/api/v1/timestamps.py), [frontend/src/components/MediaPlayerPanel.jsx](../frontend/src/components/MediaPlayerPanel.jsx), and [frontend/src/components/ChatPanel.jsx](../frontend/src/components/ChatPanel.jsx). |
| B1 | Verified | FastAPI backend scaffold and route structure in [backend/app/main.py](../backend/app/main.py). |
| B2 | Verified | LangChain/OpenAI summary and chat fallbacks in [backend/app/services/summarizer.py](../backend/app/services/summarizer.py) and [backend/app/services/chatbot.py](../backend/app/services/chatbot.py). |
| B3 | Verified | Whisper transcription integration in [backend/app/services/transcription.py](../backend/app/services/transcription.py). |
| B4 | Verified | Native pgvector vector storage and retrieval in [backend/app/models/document_chunk.py](../backend/app/models/document_chunk.py), [backend/app/services/embeddings.py](../backend/app/services/embeddings.py), and [backend/app/services/retrieval.py](../backend/app/services/retrieval.py). |
| B5 | Verified | Backend coverage gate enforced in pytest configuration and achieved in phase test runs. Latest final backend coverage: 96.41%. |
| B6 | Verified | Backend Dockerfile authored in [backend/Dockerfile](../backend/Dockerfile). Static validation note recorded in [step-report.md](../step-report.md). |
| B7 | Verified | GitHub Actions workflow authored in [.github/workflows/ci.yml](../.github/workflows/ci.yml). |
| F1 | Verified | Frontend React + Vite scaffold in [frontend/src/main.jsx](../frontend/src/main.jsx) and [frontend/src/App.jsx](../frontend/src/App.jsx). |
| F2 | Verified | Upload UI in [frontend/src/components/UploadPanel.jsx](../frontend/src/components/UploadPanel.jsx). |
| F3 | Verified | Chatbot UI in [frontend/src/components/ChatPanel.jsx](../frontend/src/components/ChatPanel.jsx). |
| F4 | Verified | Summary display in [frontend/src/components/SummaryPanel.jsx](../frontend/src/components/SummaryPanel.jsx). |
| F5 | Verified | Timestamp list UI in [frontend/src/components/TimestampPanel.jsx](../frontend/src/components/TimestampPanel.jsx). |
| F6 | Verified | Jump-to-play behavior in [frontend/src/components/MediaPlayerPanel.jsx](../frontend/src/components/MediaPlayerPanel.jsx). |
| I1 | Verified | Multi-container Docker Compose in [docker-compose.yml](../docker-compose.yml) with PostgreSQL, Redis, backend, and frontend. |
| D1 | Verified | Final README sections completed in [README.md](../README.md). |
| D2 | Verified | Final coverage evidence captured in [docs/final-coverage-evidence.md](final-coverage-evidence.md). |
| D3 | Pending | Walkthrough video must be recorded using [docs/walkthrough-script.md](walkthrough-script.md). |

## Bonus Requirements

| Requirement ID | Status | Evidence |
| --- | --- | --- |
| X1 | Pending | Not yet started. |
| X2 | Pending | Not yet started. |
| X3 | Pending | Not yet started. |
| X4 | Pending | Not yet started. |

## Validation Notes
- Static validation of [docker-compose.yml](../docker-compose.yml) succeeded with a Python YAML parser.
- Local runtime compose boot could not be executed on this machine because Docker Desktop was unavailable.
- Backend and frontend validation commands ran successfully in the available environment.
