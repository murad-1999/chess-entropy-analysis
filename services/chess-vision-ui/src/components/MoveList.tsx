

interface MoveListProps {
  moves: string[];
  currentMoveIndex: number;
  onMoveClick: (index: number) => void;
  headers?: Record<string, string>;
}

export function MoveList({ moves, currentMoveIndex, onMoveClick, headers }: MoveListProps) {
  const pairs: { num: number; white: string; black?: string; whiteIdx: number; blackIdx?: number }[] = [];
  for (let i = 0; i < moves.length; i += 2) {
    pairs.push({
      num: Math.floor(i / 2) + 1,
      white: moves[i],
      black: moves[i + 1],
      whiteIdx: i,
      blackIdx: i + 1 < moves.length ? i + 1 : undefined,
    });
  }

  return (
    <div className="flex flex-col h-full min-h-0 overflow-hidden">
      {/* Game info header */}
      {headers && (headers.White || headers.Black || headers.Event) && (
        <div className="px-5 py-4 border-b border-border/50 bg-gradient-to-r from-card/60 to-muted/30">
          {headers.Event && <p className="text-xs text-primary/80 uppercase tracking-wider font-semibold">{headers.Event}</p>}
          {(headers.White || headers.Black) && (
            <p className="text-base font-semibold mt-1 text-foreground">
              {headers.White || '?'} <span className="text-muted-foreground font-medium mx-1">vs</span> {headers.Black || '?'}
            </p>
          )}
          {headers.Result && (
            <span className="inline-block mt-2 text-xs font-mono px-2.5 py-1 rounded-lg bg-primary/10 text-primary border border-primary/20">
              {headers.Result}
            </span>
          )}
        </div>
      )}

      <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar p-2">
        {pairs.length === 0 ? (
          <p className="text-sm text-muted-foreground p-2">No moves to display</p>
        ) : (
          <div className="space-y-px">
            {pairs.map((pair) => (
              <div key={pair.num} className="flex text-base font-mono items-center">
                <span className="w-9 text-muted-foreground/60 text-right mr-2 shrink-0 text-sm">{pair.num}.</span>
                <button
                  className={`px-2.5 py-1.5 rounded-md text-left transition-colors text-sm ${
                    currentMoveIndex === pair.whiteIdx
                      ? 'bg-primary/15 text-primary font-semibold ring-1 ring-primary/20'
                      : 'hover:bg-accent/40'
                  }`}
                  onClick={() => onMoveClick(pair.whiteIdx)}
                >
                  {pair.white}
                </button>
                {pair.black && pair.blackIdx !== undefined && (
                  <button
                    className={`px-2.5 py-1.5 rounded-md text-left transition-colors ml-1 text-sm ${
                      currentMoveIndex === pair.blackIdx
                        ? 'bg-primary/15 text-primary font-semibold ring-1 ring-primary/20'
                        : 'hover:bg-accent/40'
                    }`}
                    onClick={() => onMoveClick(pair.blackIdx!)}
                  >
                    {pair.black}
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
