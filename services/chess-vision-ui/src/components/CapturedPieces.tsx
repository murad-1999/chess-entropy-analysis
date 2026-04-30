import { Chess } from 'chess.js';
import { getPieceUnicode } from '@/lib/chess-utils';

interface CapturedPiecesProps {
  fen: string;
}

const STARTING_COUNTS: Record<string, number> = {
  p: 8, n: 2, b: 2, r: 2, q: 1,
};

const PIECE_ORDER = ['q', 'r', 'b', 'n', 'p'];

export function CapturedPieces({ fen }: CapturedPiecesProps) {
  const chess = new Chess(fen);
  const board = chess.board();

  const counts: Record<string, Record<string, number>> = { w: {}, b: {} };
  for (const row of board) {
    for (const sq of row) {
      if (sq && sq.type !== 'k') {
        counts[sq.color][sq.type] = (counts[sq.color][sq.type] || 0) + 1;
      }
    }
  }

  const getCaptured = (color: 'w' | 'b') => {
    const captured: string[] = [];
    for (const p of PIECE_ORDER) {
      const onBoard = counts[color][p] || 0;
      const missing = STARTING_COUNTS[p] - onBoard;
      for (let i = 0; i < missing; i++) {
        captured.push(getPieceUnicode(color, p));
      }
    }
    return captured;
  };

  const whiteCaptured = getCaptured('w'); // white pieces captured (by black)
  const blackCaptured = getCaptured('b'); // black pieces captured (by white)

  return (
    <div className="flex flex-col gap-1 text-base">
      <div className="flex items-center gap-0.5 min-h-[24px]">
        <span className="text-sm tracking-tight opacity-80">
          {blackCaptured.join('')}
        </span>
      </div>
      <div className="flex items-center gap-0.5 min-h-[24px]">
        <span className="text-sm tracking-tight opacity-80">
          {whiteCaptured.join('')}
        </span>
      </div>
    </div>
  );
}
