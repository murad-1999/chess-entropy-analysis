import asyncio
import re
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


# ---------------------------------------------------------------------------
# Raw UCI text parser
# ---------------------------------------------------------------------------

# Pre-compiled patterns for performance when parsing many lines.
_RE_DEPTH   = re.compile(r'\bdepth\s+(\d+)')
_RE_MULTIPV = re.compile(r'\bmultipv\s+(\d+)')
_RE_CP      = re.compile(r'\bscore\s+cp\s+(-?\d+)')
_RE_MATE    = re.compile(r'\bscore\s+mate\s+(-?\d+)')
_RE_PV      = re.compile(r'\bpv\s+([a-h][1-8][a-h][1-8][qrbnQRBN]?)')


def _parse_info_line(line: str) -> dict | None:
    """
    Parse a raw Stockfish 'info' line into a structured dictionary.

    Returns a dict with keys:
        depth    (int)        – search depth
        multipv  (int)        – multi-PV index (defaults to 1 when absent)
        cp       (int | None) – score in centipawns (may be negative)
        mate     (int | None) – moves to mate, or None if not a mate score
        pv       (str | None) – first move in the principal variation

    Returns None if the line does not carry both a 'multipv' token and
    a score (cp or mate), since those lines are not analytically useful.

    Example input:
        'info depth 18 multipv 1 score cp -34 nodes 12345 pv e2e4 e7e5'
    Example output:
        {'depth': 18, 'multipv': 1, 'cp': -34, 'mate': None, 'pv': 'e2e4'}
    """
    if not line.startswith('info'):
        return None

    # Require a score of some kind (cp or mate).
    cp_match   = _RE_CP.search(line)
    mate_match = _RE_MATE.search(line)
    if cp_match is None and mate_match is None:
        return None

    # Require multipv to be present (filters out non-analysis info lines).
    multipv_match = _RE_MULTIPV.search(line)
    if multipv_match is None:
        return None

    depth_match = _RE_DEPTH.search(line)
    pv_match    = _RE_PV.search(line)

    return {
        'depth':   int(depth_match.group(1)) if depth_match else 0,
        'multipv': int(multipv_match.group(1)),
        'cp':      int(cp_match.group(1))   if cp_match   else None,
        'mate':    int(mate_match.group(1)) if mate_match else None,
        'pv':      pv_match.group(1)        if pv_match   else None,
    }
