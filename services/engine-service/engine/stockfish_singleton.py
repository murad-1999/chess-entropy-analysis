import asyncio
import chess
import chess.engine
from engine.uci_client import analyse_position
import math

class StockfishSingleton:
    def __init__(self, binary_path="/usr/local/bin/stockfish"):
        self.binary_path = binary_path
        self._engine = None
        self._lock = asyncio.Lock()

    async def _get_engine(self):
        if self._engine is None:
            transport, engine = await chess.engine.popen_uci(self.binary_path)
            self._engine = engine
        return self._engine

    async def analyze_position(self, fen: str, depth: int = 15):
        async with self._lock:
            engine = await self._get_engine()
            board = chess.Board(fen)
            limit = chess.engine.Limit(depth=depth)
            
            # Using custom timeout wrapper
            info = await analyse_position(engine, board, limit)
            
            score = info.get("score")
            cp = None
            mate = None
            wdl = None
            winning_chances = None

            if score is not None:
                pov_score = score.pov(chess.WHITE)
                if pov_score.is_mate():
                    mate = pov_score.mate()
                else:
                    cp = pov_score.score()

                # Get WDL (Win/Draw/Loss) stats using python-chess WDL model built-in if available,
                # else manually estimate winning chances:
                try:
                    wdl_stats = pov_score.wdl()
                    # wdl_stats returns expected value [0, 1000]
                    winning_chances = wdl_stats.expectation() / 1000.0
                except Exception:
                    # Fallback estimating using typical logistic curve if python-chess version doesn't support wdl
                    if cp is not None:
                        winning_chances = 1 / (1 + 10 ** (-cp / 400))
                    elif mate is not None:
                        winning_chances = 1.0 if mate > 0 else 0.0

            return {
                "position": fen,
                "centipawns": cp,
                "mate": mate,
                "winning_chances": winning_chances
            }

    async def close(self):
        if self._engine is not None:
            await self._engine.quit()

stockfish_singleton = StockfishSingleton()
