import io
import httpx
import chess.pgn
import asyncio

from engine.stockfish_singleton import stockfish_singleton

TASK_STORE = {}


def _top_line_to_eval(analysis_lines: list[dict]) -> dict:
    """
    Transform deep_analyze output (list of PV dicts) into the flat
    EngineEval shape the frontend expects:
        { centipawns, winning_chances, mate }
    """
    if not analysis_lines:
        return {"centipawns": 0, "winning_chances": 0.5, "mate": None}

    top = analysis_lines[0]  # multipv=1 is the best line
    cp = top.get("cp")
    mate = top.get("mate")

    # Compute winning chances (logistic model, same as StockfishSingleton._wdl_from_score)
    if mate is not None:
        winning_chances = 1.0 if mate > 0 else 0.0
    elif cp is not None:
        winning_chances = 1 / (1 + 10 ** (-cp / 400))
    else:
        winning_chances = 0.5

    return {
        "centipawns": cp,
        "winning_chances": winning_chances,
        "mate": mate,
    }


async def cleanup_task(task_id: str, delay_seconds: int = 3600):
    """Safely removes the task from memory after the specified delay."""
    await asyncio.sleep(delay_seconds)
    TASK_STORE.pop(task_id, None)

def parse_fens_cpu_bound(pgn_text: str):
    """Synchronous CPU-bound PGN paring helper to be offloaded."""
    pgn_io = io.StringIO(pgn_text)
    game = chess.pgn.read_game(pgn_io)
    
    if not game:
        return None
        
    fens = []
    board = game.board()
    fens.append(board.fen())
    for move in game.mainline_moves():
        board.push(move)
        fens.append(board.fen())
    
    return fens

async def process_pgn(task_id: str, url: str | None = None, pgn_string: str | None = None):
    try:
        # Step 1: Fetching or loading string
        TASK_STORE[task_id] = {"status": "fetching"}
        
        pgn_text = None
        if url:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    pgn_text = response.text
            except Exception:
                TASK_STORE[task_id] = {"status": "failed", "error": "HTTP Error"}
                return
        elif pgn_string:
            pgn_text = pgn_string
        else:
            TASK_STORE[task_id] = {"status": "failed", "error": "No data source provided."}
            return

        # Step 2: Parsing (Offloaded to a thread pool)
        TASK_STORE[task_id] = {"status": "parsing"}
        # Await the execution of CPU blocking code inside a separate thread!
        fens = await asyncio.to_thread(parse_fens_cpu_bound, pgn_text)
        
        if not fens:
            TASK_STORE[task_id] = {"status": "failed", "error": "Failed to parse PGN"}
            return

        # Step 3: Analyzing
        TASK_STORE[task_id] = {"status": "analyzing"}
        
        list_of_analysis_data = []
        if stockfish_singleton is not None:
            for fen in fens:
                try:
                    analysis = await stockfish_singleton.deep_analyze(fen, depth=15, multipv=5)
                    list_of_analysis_data.append(analysis)
                except Exception as e:
                    # In case of custom EngineTimeoutError throwing during analysis
                    TASK_STORE[task_id] = {"status": "failed", "error": str(e)}
                    return
        else:
            # Polyfill if singleton isn't imported successfully yet
            list_of_analysis_data = [{"position": fen, "eval": "N/A"} for fen in fens]

        # Step 4: Completion
        # Convert each position's raw PV list into the flat EngineEval shape
        # { centipawns, winning_chances, mate } that the frontend expects.
        engine_evals = [_top_line_to_eval(analysis) for analysis in list_of_analysis_data]
        TASK_STORE[task_id] = {"status": "completed", "results": engine_evals}
        
    finally:
        # Step 5: Self-destruction scheduling
        # Triggers a delayed cleanup so memory doesn't leak whether it failed or succeeded!
        asyncio.create_task(cleanup_task(task_id))
