import asyncio
import chess.engine
from core.exceptions import EngineTimeoutError

# No FastAPI imports here! Strict separation of concerns is maintained.

async def analyse_position(engine_protocol, board: chess.Board, limit: chess.engine.Limit):
    """
    Wrapper for Stockfish analyse() call that maps underlying 
    asyncio timeouts or engine crash errors to our custom EngineTimeoutError.
    """
    try:
        return await engine_protocol.analyse(board, limit)
    except (asyncio.TimeoutError, chess.engine.EngineTerminatedError) as e:
        raise EngineTimeoutError(f"Engine analysis failed or timed out: {str(e)}") from e
