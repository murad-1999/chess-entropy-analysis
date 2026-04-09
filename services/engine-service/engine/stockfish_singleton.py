import asyncio
import math
import chess
import chess.engine

from engine.uci_client import _parse_info_line
from core.exceptions import EngineTimeoutError


class StockfishSingleton:
    def __init__(self, binary_path: str = "/usr/local/bin/stockfish"):
        self.binary_path = binary_path
        self._engine: chess.engine.UciProtocol | None = None
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get_engine(self) -> chess.engine.UciProtocol:
        """Lazily spawn the Stockfish process (singleton pattern)."""
        if self._engine is None:
            _, engine = await chess.engine.popen_uci(self.binary_path)
            self._engine = engine
        return self._engine

    async def _reset_game_state(self, engine: chess.engine.UciProtocol) -> None:
        """Send 'ucinewgame' to clear Stockfish's transposition table."""
        await engine.ping()          # ensures the previous command finished
        engine.send_line("ucinewgame")
        await engine.ping()          # wait until Stockfish has processed it

    @staticmethod
    def _wdl_from_score(pov_score: chess.engine.PovScore) -> float | None:
        """
        Convert a PovScore (White POV) to a winning-chance probability in [0, 1].
        Falls back to a logistic approximation when WDL tables are unavailable.
        """
        try:
            return pov_score.wdl().expectation() / 1000.0
        except Exception:
            if pov_score.is_mate():
                mate = pov_score.mate()
                return 1.0 if mate > 0 else 0.0
            cp = pov_score.score()
            if cp is not None:
                return 1 / (1 + 10 ** (-cp / 400))
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def deep_analyze(
        self,
        fen: str,
        depth: int = 15,
        multipv: int = 5,
    ) -> list[dict]:
        """
        Run a deep, multi-variation analysis of a position.

        Configures the engine for ``multipv`` lines, searches to ``depth``,
        collects every raw 'info' line emitted by Stockfish, parses them with
        ``_parse_info_line``, and returns only the final (deepest) result for
        each PV rank, sorted ascending by multipv index.

        Args:
            fen:     FEN string for the position to analyse.
            depth:   Search depth (plies).
            multipv: Number of best moves to return.

        Returns:
            List of dicts, one per PV rank, each containing:
                multipv  (int)        – rank (1 = best)
                depth    (int)        – depth reached
                cp       (int | None) – centipawn score
                mate     (int | None) – moves to mate
                pv       (str | None) – first move of the principal variation
        """
        async with self._lock:
            engine = await self._get_engine()
            await self._reset_game_state(engine)

            board = chess.Board(fen)

            # Accumulate *all* parsed info lines so we can keep the deepest
            # entry for each multipv rank (Stockfish emits incremental updates).
            best_per_rank: dict[int, dict] = {}

            try:
                with await engine.analysis(
                    board,
                    chess.engine.Limit(depth=depth),
                    multipv=multipv,
                ) as analysis:
                    async for info in analysis:
                        # chess.engine wraps info as a dict; convert to raw
                        # text is not available — use the structured info dict
                        # directly since python-chess already parsed it.
                        parsed = _extract_from_info_dict(info)
                        if parsed is not None:
                            rank = parsed["multipv"]
                            # Keep the deepest seen result for every rank.
                            prev = best_per_rank.get(rank)
                            if prev is None or parsed["depth"] >= prev["depth"]:
                                best_per_rank[rank] = parsed
            except (asyncio.TimeoutError, chess.engine.EngineTerminatedError) as exc:
                raise EngineTimeoutError(
                    f"deep_analyze failed or timed out: {exc}"
                ) from exc

            return sorted(best_per_rank.values(), key=lambda r: r["multipv"])

    async def fast_eval(
        self,
        fen: str,
        time_limit_ms: int = 100,
    ) -> dict:
        """
        Quick single-line evaluation suitable for real-time UI feedback.

        Searches for exactly ``time_limit_ms`` milliseconds with multipv=1.

        Args:
            fen:           FEN string for the position to evaluate.
            time_limit_ms: Time budget in milliseconds.

        Returns:
            Dict with keys:
                position         (str)        – input FEN
                pv               (str | None) – best move (UCI notation)
                cp               (int | None) – centipawn score (White POV)
                mate             (int | None) – moves to mate (White POV)
                winning_chances  (float|None) – probability in [0, 1] for White
        """
        async with self._lock:
            engine = await self._get_engine()
            await self._reset_game_state(engine)

            board = chess.Board(fen)
            time_sec = time_limit_ms / 1000.0

            cp: int | None = None
            mate: int | None = None
            pv: str | None = None
            winning_chances: float | None = None

            try:
                with await engine.analysis(
                    board,
                    chess.engine.Limit(time=time_sec),
                    multipv=1,
                ) as analysis:
                    async for info in analysis:
                        parsed = _extract_from_info_dict(info)
                        if parsed is not None:
                            cp   = parsed["cp"]
                            mate = parsed["mate"]
                            pv   = parsed["pv"]

                # Compute winning chances from the final score object if available.
                result = await engine.analyse(
                    board,
                    chess.engine.Limit(time=time_sec),
                )
                score = result.get("score")
                if score is not None:
                    pov = score.pov(chess.WHITE)
                    if pov.is_mate():
                        mate = pov.mate()
                        cp = None
                    else:
                        cp = pov.score()
                    winning_chances = self._wdl_from_score(pov)
                    pv = pv or (
                        result["pv"][0].uci() if result.get("pv") else None
                    )

            except (asyncio.TimeoutError, chess.engine.EngineTerminatedError) as exc:
                raise EngineTimeoutError(
                    f"fast_eval failed or timed out: {exc}"
                ) from exc

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
            await self._engine.quit()
            self._engine = None


# ---------------------------------------------------------------------------
# Module-level helper  (bridges python-chess info dict → our schema)
# ---------------------------------------------------------------------------

def _extract_from_info_dict(info: chess.engine.InfoDict) -> dict | None:
    """
    Convert a python-chess ``InfoDict`` into our canonical parsed-line schema.

    This mirrors what ``_parse_info_line`` does for raw text, but operates on
    the already-structured dict that python-chess produces during streaming
    analysis — avoiding the need to reconstruct the raw UCI string.

    Returns None if the info dict lacks a score (not analytically useful).
    """
    score = info.get("score")
    if score is None:
        return None

    multipv: int = info.get("multipv", 1)
    depth: int = info.get("depth", 0)

    pov = score.pov(chess.WHITE)
    cp: int | None = None
    mate: int | None = None

    if pov.is_mate():
        mate = pov.mate()
    else:
        cp = pov.score()

    pv_moves = info.get("pv", [])
    first_move: str | None = pv_moves[0].uci() if pv_moves else None

    return {
        "multipv": multipv,
        "depth":   depth,
        "cp":      cp,
        "mate":    mate,
        "pv":      first_move,
    }


# ---------------------------------------------------------------------------
# Global singleton instance
# ---------------------------------------------------------------------------

stockfish_singleton = StockfishSingleton()
