interface EvalBarProps {
  evaluation: number | null;
  winningChances?: number | null;
  mate?: number | null;
  flipped: boolean;
}

export function EvalBar({ evaluation, winningChances, mate, flipped }: EvalBarProps) {
  let whitePercent = 50;
  let displayText = '0.0';

  if (mate != null && mate !== 0) {
    whitePercent = mate > 0 ? 100 : 0;
    displayText = `M${Math.abs(mate)}`;
  } else if (winningChances != null) {
    whitePercent = winningChances * 100;
    if (evaluation != null) {
      const sign = evaluation > 0 ? '+' : '';
      displayText = `${sign}${evaluation.toFixed(1)}`;
    }
  } else if (evaluation != null) {
    const clamped = Math.max(-5, Math.min(5, evaluation));
    whitePercent = 50 + (clamped / 5) * 50;
    const sign = evaluation > 0 ? '+' : '';
    displayText = Math.abs(evaluation) >= 10
      ? (evaluation > 0 ? '+10' : '-10')
      : `${sign}${evaluation.toFixed(1)}`;
  }

  const displayPercent = flipped ? 100 - whitePercent : whitePercent;
  const favorsWhite = mate != null && mate !== 0 ? mate > 0 : (evaluation != null ? evaluation >= 0 : true);

  return (
    <div className="flex flex-col items-center w-8 rounded-lg overflow-hidden border border-black/20 dark:border-white/10 h-full min-h-[240px] shadow-inner bg-black">
      {/* Black side */}
      <div
        className="w-full transition-all duration-500 ease-out flex items-start justify-center relative shadow-[inset_0_-2px_6px_rgba(0,0,0,0.4)]"
        style={{
          height: `${100 - displayPercent}%`,
          backgroundImage: 'linear-gradient(to bottom, #302E2B, #1B1A19)',
        }}
      >
        {!favorsWhite && (
          <span className="text-[11px] font-mono text-white/90 drop-shadow-md mt-1.5 font-bold tracking-tight">{displayText}</span>
        )}
      </div>
      {/* White side */}
      <div
        className="w-full transition-all duration-500 ease-out flex items-end justify-center relative shadow-[inset_0_2px_6px_rgba(0,0,0,0.15)]"
        style={{
          height: `${displayPercent}%`,
          backgroundImage: 'linear-gradient(to bottom, #FFFFFF, #E6E6E6)',
        }}
      >
        {favorsWhite && (
          <span className="text-[11px] font-mono mb-1.5 font-bold tracking-tight text-[#1B1A19] drop-shadow-sm">
            {displayText}
          </span>
        )}
      </div>
    </div>
  );
}
