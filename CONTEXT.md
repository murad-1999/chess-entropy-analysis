# `context.md` - Chess Entropy Analysis

## 🎯 Project Overview
This project is a containerized, microservices-based web application designed to calculate and visualize chess board complexity. Instead of just showing standard evaluation (who is winning), it calculates the "Shannon Entropy" and "Tension Matrix" of a position to visualize which squares are under the most pressure using a dynamic heatmap.

## 🏗️ Architecture & Tech Stack
This is a monorepo containing decoupled frontend and backend services, orchestrated via Docker Compose.

* **Frontend (`services/chess-vision-dark/`):** React, Vite, TypeScript, TailwindCSS. Built as a static SPA, interacting purely via REST API.
* **Backend (`services/engine-service/`):** Python 3.11, FastAPI. Acts as an asynchronous API wrapper and UCI parser for the C++ Stockfish engine.
* **Engine (`stockfish`):** Stockfish 16.1 (AVX2 optimized binary for Linux), running as a hidden child process inside the backend Docker container.
* **Infrastructure:** Docker, Docker Compose.

## 📂 Directory Structure
```text
chess-entropy-analysis/
├── docker-compose.yml       # Orchestrates frontend and backend networks
├── .gitmodules              # Tracks Lovable frontend submodule
├── context.md               # AI context and rules (This file)
└── services/
    ├── chess-vision-dark/   # Vite/React Frontend
    └── engine-service/      # FastAPI Backend
        ├── api/             # Routes (endpoints), background tasks, exceptions
        ├── core/            # Pydantic settings, custom Python exceptions
        ├── engine/          # uci_client.py (Singleton Stockfish wrapper)
        ├── schemas/         # Pydantic request/response models
        ├── tests/           # Pytest suite with mocked network calls
        ├── requirements.txt
        └── Dockerfile       # Pulls AVX2 binary, runs as non-root appuser
```

## ⚙️ Core Backend Mechanics (`engine-service`)
The backend is highly optimized for performance and resource protection.
1.  **The Singleton Engine:** Stockfish is initialized ONCE on application startup. API routes use an `asyncio.Lock()` to queue requests. We never spawn multiple engine processes to prevent CPU thrashing.
2.  **Strict Validation:** FEN strings are validated mathematically using the `python-chess` library inside Pydantic field validators, *never* via Regex.
3.  **State Bleed Prevention:** The `uci_client.py` MUST send the `ucinewgame` command before analyzing any position to clear engine hash tables.
4.  **Async Ingestion:** Lichess URLs or raw PGN strings are sent to `POST /import`. This triggers a non-blocking `BackgroundTask`. Heavy PGN parsing happens in `asyncio.to_thread()`.
5.  **Memory Management:** Background tasks update an in-memory `TASK_STORE` dictionary. A cleanup function automatically purges finished tasks after 1 hour to prevent memory leaks.

## 🎨 Core Frontend Mechanics (`chess-vision-dark`)
The UI is a "dumb" client that strictly reflects backend state.
1.  **Environment:** API calls must route through `import.meta.env.VITE_API_URL` (defaulting to `http://localhost:8000`).
2.  **Polling:** For game imports, the UI receives a `task_id` and must poll the `GET /task/{id}` endpoint every 2000ms until the status is `completed`.
3.  **Visual Mapping:** The UI receives a Tension Matrix (array of square pressures) and maps it to the 64-square CSS grid, dynamically updating Tailwind background colors to create the heatmap.

## 🤖 Strict Rules for AI Assistants
When writing or editing code for this project, you MUST adhere to the following rules:
* **No Cross-Contamination:** Never put Python engine logic in the `api/` folder. Never put web routing logic in the `engine/` folder.
* **No Blocking Code:** Never run heavy CPU tasks (like parsing massive PGNs with `python-chess`) directly on the main async event loop.
* **Test Isolation:** When writing tests in `pytest`, you MUST use `unittest.mock.patch` to mock any external HTTP calls (`httpx`) and background worker functions. Do not execute real Stockfish logic in routing tests.
* **Security:** Ensure the Docker container always runs as a non-root user (`appuser`). Keep CORS locked to the frontend origin.

*** ### How to use this:
If you are using Cursor, save this text as `.cursorrules` in your root directory. The AI will automatically read it before every prompt. If you are using another tool or a standard chat window, just upload `context.md` or paste it in at the start of a new session so the AI instantly knows the exact structural boundaries of your project.