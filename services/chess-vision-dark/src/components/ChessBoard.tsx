import { useState, useEffect, useRef } from 'react';
import { Chess } from 'chess.js';
import { ChessPiece } from '@/components/ChessPiece';

interface ChessBoardProps {
  fen: string;
  flipped: boolean;
  lastMove?: { from: string; to: string } | null;
}

const FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
const RANKS = [8, 7, 6, 5, 4, 3, 2, 1];

function getSquareCoords(square: string, flipped: boolean): { col: number; row: number } {
  const file = square[0];
  const rank = parseInt(square[1]);
  const col = flipped ? 7 - FILES.indexOf(file) : FILES.indexOf(file);
  const row = flipped ? rank - 1 : 8 - rank;
  return { col, row };
}

export function ChessBoard({ fen, flipped, lastMove }: ChessBoardProps) {
  const chess = new Chess(fen);
  const board = chess.board();

  const ranks = flipped ? [...RANKS].reverse() : RANKS;
  const files = flipped ? [...FILES].reverse() : FILES;

  // Track animation state
  const [animating, setAnimating] = useState(false);
  const [animOffset, setAnimOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const prevLastMoveRef = useRef<{ from: string; to: string } | null | undefined>(undefined);

  useEffect(() => {
    const prev = prevLastMoveRef.current;
    prevLastMoveRef.current = lastMove;

    // Only animate when lastMove actually changes to a new move
    if (
      lastMove &&
      (!prev || prev.from !== lastMove.from || prev.to !== lastMove.to)
    ) {
      const from = getSquareCoords(lastMove.from, flipped);
      const to = getSquareCoords(lastMove.to, flipped);
      const dx = (from.col - to.col) * 100; // percentage of one square
      const dy = (from.row - to.row) * 100;

      // Start at the origin square offset
      setAnimOffset({ x: dx, y: dy });
      setAnimating(false);

      // Trigger transition to (0,0) on next frame
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setAnimOffset({ x: 0, y: 0 });
          setAnimating(true);
        });
      });

      // Clear animation flag after transition completes
      const timer = setTimeout(() => setAnimating(false), 300);
      return () => clearTimeout(timer);
    }
  }, [lastMove, flipped]);

  return (
    <div className="grid grid-cols-8 grid-rows-[repeat(8,1fr)] border border-border rounded-md overflow-hidden aspect-square w-full max-w-[672px]">
      {ranks.map((rank, ri) =>
        files.map((file, fi) => {
          const r = 8 - rank;
          const c = FILES.indexOf(file);
          const sq = board[r][c];
          const isLight = (ri + fi) % 2 === 0;
          const squareName = `${file}${rank}`;
          const isDestination = lastMove && squareName === lastMove.to;

          return (
            <div
              key={squareName}
              className="relative flex items-center justify-center select-none aspect-square overflow-visible"
              style={{
                backgroundColor: isLight
                  ? 'hsl(var(--board-light))'
                  : 'hsl(var(--board-dark))',
              }}
            >
              {fi === 0 && (
                <span
                  className="absolute top-0.5 left-0.5 z-20 text-xs leading-none font-semibold"
                  style={{ color: isLight ? 'hsl(var(--board-dark))' : 'hsl(var(--board-light))' }}
                >
                  {rank}
                </span>
              )}
              {ri === 7 && (
                <span
                  className="absolute bottom-0.5 right-0.5 z-20 text-xs leading-none font-semibold"
                  style={{ color: isLight ? 'hsl(var(--board-dark))' : 'hsl(var(--board-light))' }}
                >
                  {file}
                </span>
              )}
              {sq && (
                <div
                  className="z-20"
                  style={
                    isDestination
                      ? {
                          transform: `translate(${animOffset.x}%, ${animOffset.y}%)`,
                          transition: animating ? 'transform 0.25s cubic-bezier(0.25, 0.1, 0.25, 1)' : 'none',
                        }
                      : undefined
                  }
                >
                  <ChessPiece piece={sq.type} color={sq.color} />
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );
}
