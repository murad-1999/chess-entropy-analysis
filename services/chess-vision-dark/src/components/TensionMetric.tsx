import React from 'react';

interface TensionMetricProps {
  currentEntropy: number;
}

export const TensionMetric: React.FC<TensionMetricProps> = ({ currentEntropy }) => {
  let label = 'Calm';
  let colorClasses = 'text-slate-500 border-slate-500 bg-slate-500/10';

  if (currentEntropy >= 1.5) {
    label = 'Chaotic';
    colorClasses = 'text-red-500 border-red-500 bg-red-500/10 shadow-[0_0_10px_rgba(239,68,68,0.5)]';
  } else if (currentEntropy >= 0.5) {
    label = 'Complex';
    colorClasses = 'text-amber-500 border-amber-500 bg-amber-500/10';
  }

  return (
    <div className={`inline-flex items-center justify-center px-4 py-1.5 rounded-full border text-base font-semibold transition-colors duration-300 ${colorClasses}`}>
      <span className="mr-2 uppercase tracking-wider text-xs opacity-80">{label}</span>
      <span>{currentEntropy.toFixed(2)}</span>
    </div>
  );
};
