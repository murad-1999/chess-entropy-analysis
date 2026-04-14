import asyncio
import re
from core.exceptions import EngineTimeoutError

# Pre-compiled patterns for performance
_RE_DEPTH   = re.compile(r'\bdepth\s+(\d+)')
_RE_MULTIPV = re.compile(r'\bmultipv\s+(\d+)')
_RE_CP      = re.compile(r'\bscore\s+cp\s+(-?\d+)')
_RE_MATE    = re.compile(r'\bscore\s+mate\s+(-?\d+)')
_RE_PV      = re.compile(r'\bpv\s+(.*)')

def _parse_info_line(line: str) -> dict | None:
    """
    Parse a raw Stockfish 'info' line into a structured dictionary.
    """
    if not line.startswith('info'):
        return None

    cp_match   = _RE_CP.search(line)
    mate_match = _RE_MATE.search(line)
    if cp_match is None and mate_match is None:
        return None

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

class UCIClient:
    def __init__(self, binary_path: str = "/usr/local/bin/stockfish"):
        self.binary_path = binary_path
        self._engine: asyncio.subprocess.Process | None = None
        self._lock = asyncio.Lock()

    async def _get_engine(self) -> asyncio.subprocess.Process:
        """Lazily spawn the Stockfish process using raw asyncio subprocess."""
        if self._engine is None:
            self._engine = await asyncio.create_subprocess_exec(
                self.binary_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # Hardware Allocation (RAM & Threads)
            self._engine.stdin.write(b"setoption name Threads value 4\n")
            self._engine.stdin.write(b"setoption name Hash value 256\n")
            self._engine.stdin.write(b"isready\n")
            await self._engine.stdin.drain()

            # Ensure Safe Boot: block until readyok
            while True:
                line = await self._engine.stdout.readline()
                if not line:
                    break
                if line.decode('utf-8').strip() == 'readyok':
                    break
                    
        return self._engine

    async def _reset_game_state(self, process: asyncio.subprocess.Process) -> None:
        """Send 'ucinewgame' to clear Stockfish's transposition table."""
        process.stdin.write(b"ucinewgame\n")
        process.stdin.write(b"isready\n")
        await process.stdin.drain()
        
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            if line.decode('utf-8').strip() == 'readyok':
                break

    async def deep_analyze(self, fen: str, depth: int = 15, multipv: int = 3) -> list[dict]:
        """
        Run a deep, multi-variation analysis of a position using raw UCI text.
        """
        async with self._lock:
            try:
                process = await self._get_engine()
                await self._reset_game_state(process)
    
                # Determine turn constraint (FEN POV adjustment)
                board_parts = fen.split()
                is_white_turn = (board_parts[1] == 'w') if len(board_parts) > 1 else True
    
                best_per_rank: dict[int, dict] = {}
    
                process.stdin.write(f"position fen {fen}\n".encode())
                process.stdin.write(f"setoption name MultiPV value {multipv}\n".encode())
                process.stdin.write(f"go depth {depth}\n".encode())
                await process.stdin.drain()
    
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    decoded = line.decode('utf-8').strip()
                    if decoded.startswith('bestmove'):
                        break
                        
                    parsed = _parse_info_line(decoded)
                    if parsed is not None:
                        # Raw UCI returns CP relative to the side to move. Normalize to White POV.
                        if not is_white_turn:
                            if parsed["cp"] is not None:
                                parsed["cp"] = -parsed["cp"]
                            if parsed["mate"] is not None:
                                parsed["mate"] = -parsed["mate"]
                        
                        rank = parsed["multipv"]
                        prev = best_per_rank.get(rank)
                        if prev is None or parsed["depth"] >= prev["depth"]:
                            best_per_rank[rank] = parsed
                            
            except Exception as exc:
                raise EngineTimeoutError(f"deep_analyze failed or timed out: {exc}") from exc

            return sorted(best_per_rank.values(), key=lambda r: r["multipv"])

    async def fast_eval(self, fen: str, time_limit_ms: int = 100) -> dict:
        """
        Quick single-line evaluation suitable for real-time UI feedback.
        """
        async with self._lock:
            try:
                process = await self._get_engine()
                await self._reset_game_state(process)
    
                board_parts = fen.split()
                is_white_turn = (board_parts[1] == 'w') if len(board_parts) > 1 else True
    
                process.stdin.write(f"position fen {fen}\n".encode())
                process.stdin.write(b"setoption name MultiPV value 1\n")
                process.stdin.write(f"go movetime {time_limit_ms}\n".encode())
                await process.stdin.drain()
    
                cp: int | None = None
                mate: int | None = None
                pv: str | None = None
    
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    decoded = line.decode('utf-8').strip()
                    if decoded.startswith('bestmove'):
                        parts = decoded.split()
                        if len(parts) >= 2 and not pv:
                            pv = parts[1]
                        break
                    
                    parsed = _parse_info_line(decoded)
                    if parsed is not None:
                        if not is_white_turn:
                            if parsed["cp"] is not None:
                                parsed["cp"] = -parsed["cp"]
                            if parsed["mate"] is not None:
                                parsed["mate"] = -parsed["mate"]
                        cp = parsed["cp"]
                        mate = parsed["mate"]
                        pv = parsed["pv"] or pv
    
                winning_chances: float | None = None
                if mate is not None:
                    winning_chances = 1.0 if mate > 0 else 0.0
                elif cp is not None:
                    winning_chances = 1 / (1 + 10 ** (-cp / 400))
                    
            except Exception as exc:
                raise EngineTimeoutError(f"fast_eval failed or timed out: {exc}") from exc

            return {
                "position": fen,
                "pv": pv,
                "cp": cp,
                "mate": mate,
                "winning_chances": winning_chances,
            }

    async def close(self) -> None:
        """Gracefully terminate the Stockfish process."""
        if self._engine is not None:
            self._engine.terminate()
            try:
                await asyncio.wait_for(self._engine.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                self._engine.kill()
            self._engine = None
