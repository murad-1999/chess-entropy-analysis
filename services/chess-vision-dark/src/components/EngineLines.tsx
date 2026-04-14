import React from 'react';
import { EngineLine } from '@/services/api';

interface EngineLinesProps {
  lines: EngineLine[];
}

export const EngineLines: React.FC<EngineLinesProps> = ({ lines }) => {
  if (!lines || lines.length === 0) return null;

  return (
    <div className="flex flex-col gap-2 mt-2">
      <div className="flex items-center gap-2 px-3">
        <span className="text-primary/90 font-semibold tracking-wide uppercase text-[10px]">Stockfish Analysis</span>
        <div className="h-[1px] flex-1 bg-border/40"></div>
      </div>
      <div className="flex flex-col gap-1.5">
        {lines.map((line, idx) => {
          const rawCp = line.cp_score ?? line.centipawn ?? line.cp;
          const score = rawCp != null && !isNaN(parseFloat(String(rawCp)))
            ? (parseFloat(String(rawCp)) / 100).toFixed(2)
            : null;
          const mate = line.mate_score ?? line.mate;
          
          const displayScore = mate !== null && mate !== undefined
            ? `#${mate}`
            : score !== null 
              ? (parseFloat(score) > 0 ? `+${score}` : score)
              : '0.00';

          return (
            <div 
              key={idx} 
              className="group flex items-start gap-3 px-3 py-2.5 bg-muted/20 hover:bg-muted/40 border border-border/30 rounded-xl transition-all duration-200"
            >
              <div className="flex flex-col items-center justify-center min-w-[48px] h-full py-0.5">
                <span className={`text-xs font-bold font-mono px-1.5 py-0.5 rounded ${
                  mate !== null ? 'bg-primary/20 text-primary' : 'bg-muted/60 text-muted-foreground'
                }`}>
                  {displayScore}
                </span>
                <span className="text-[9px] uppercase font-bold text-muted-foreground/50 mt-1">Line {idx + 1}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-mono text-foreground/80 leading-relaxed break-words">
                  {line.pv || 'Calculating...'}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
