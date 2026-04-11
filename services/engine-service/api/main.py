import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

from api.tasks import process_pgn, TASK_STORE
from api.exceptions import validation_exception_handler, engine_timeout_handler
from core.exceptions import EngineTimeoutError
from engine.stockfish_singleton import stockfish_singleton

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(EngineTimeoutError, engine_timeout_handler)


class PGNImportRequest(BaseModel):
    url: str | None = None
    pgn_string: str | None = None

@app.post("/import", status_code=status.HTTP_202_ACCEPTED)
async def import_pgn(request: PGNImportRequest, background_tasks: BackgroundTasks):
    if not request.url and not request.pgn_string:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide either url or pgn_string.")

    task_id = str(uuid.uuid4())
    TASK_STORE[task_id] = {"status": "pending"}
    
    background_tasks.add_task(process_pgn, task_id=task_id, url=request.url, pgn_string=request.pgn_string)
    
    return {"task_id": task_id, "message": "Import started"}

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    if task_id not in TASK_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return TASK_STORE[task_id]


# ---------------------------------------------------------------------------
# Synchronous analysis endpoint  (single-position, blocking response)
# ---------------------------------------------------------------------------

class AnalysisRequest(BaseModel):
    fen: str = Field(
        ...,
        description="FEN string of the position to analyse.",
        examples=["rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"],
    )
    depth: int = Field(15, ge=1, le=30, description="Search depth for deep analysis.")
    multipv: int = Field(5, ge=1, le=10, description="Number of top moves returned by deep analysis.")

@app.post("/analyze")
async def analyze_position(request: AnalysisRequest):
    """
    Analyse a single chess position for JIT evaluation.
    Evaluates the specific FEN and returns a JSON array of the top engine lines.
    """
    moves = await stockfish_singleton.deep_analyze(
        fen=request.fen,
        depth=request.depth,
        multipv=request.multipv,
    )
    
    # Format the result as a JSON array of the top engine lines
    formatted_moves = [
        {
            "uci_move": m["pv"],
            "centipawn": m["cp"],
            "mate": m["mate"]
        }
        for m in moves
    ]
    
    return formatted_moves
