import React from 'react';

export const HeatmapLegend: React.FC = () => {
  return (
    <div className="flex flex-col items-center gap-1.5 w-full mt-1 px-2">
      <div className="flex justify-between w-full text-xs text-muted-foreground font-medium px-1">
        <span>Low Tension</span>
        <span>High Tension</span>
      </div>
      <div 
        className="w-full h-3 rounded-full overflow-hidden shadow-inner border border-black/20 dark:border-white/10"
        style={{
          background: 'linear-gradient(to right, rgb(30, 64, 175), rgb(59, 130, 246), rgb(217, 119, 6), rgb(239, 68, 68), rgb(236, 72, 153))'
        }}
      />
    </div>
  );
};
