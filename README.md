service 1: The Engine (Backend)
Tech Stack: FastAPI, python-chess, Stockfish 16.1 (AVX2 Linux Binary).

Concurrency: Singleton pattern. Only one Stockfish process is kept alive to protect CPU. All requests use an asyncio.Lock to queue up.

Endpoints:

POST /analyze: Sync evaluation of a FEN.

POST /import: Async ingestion of Lichess URLs or raw PGN strings via BackgroundTasks.

GET /task/{id}: Polling endpoint for background task status.

Safety Features:

Legal Validation: Uses python-chess (not just Regex) to ensure positions are physically legal before reaching the engine.

Memory Management: TASK_STORE has a 1-hour TTL cleanup task to prevent RAM leaks.

Security: Runs as a non-root appuser. CORS restricted to localhost:5173.

Decoupled Logic: Engine layer raises EngineTimeoutError; API layer maps it to 504 Gateway Timeout.

Service 2: The GUI (Frontend)
Tech Stack: React, Vite, Tailwind (Exported from Lovable).

Integration: Linked as a Git Submodule.

Status: Needs the "Logic Bridge" to replace mock data with real fetch() calls to the engine-service.
