import React from 'react';

interface HeatmapOverlayProps {
  tensionMatrix: Record<string, number>;
  flipped?: boolean;
}

export const HeatmapOverlay: React.FC<HeatmapOverlayProps> = React.memo(({ tensionMatrix, flipped = false }) => {
  const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
  const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];

  const displayFiles = flipped ? [...files].reverse() : files;
  const displayRanks = flipped ? [...ranks].reverse() : ranks;

  const getHeatmapColor = (value: number) => {
    const v = Math.min(1, Math.max(0, value));
    
    // Custom colormap: Deep Blue -> Light Blue -> Orange -> Red
    const colors = [
      [30, 64, 175],   // 0.0: Deep Blue
      [59, 130, 246],  // 0.25: Blue
      [217, 119, 6],   // 0.5: Golden/Orange
      [239, 68, 68],   // 0.75: Red
      [236, 72, 153],  // 1.0: Pinkish Red
    ];
    
    const index = v * (colors.length - 1);
    const i = Math.floor(index);
    const f = index - i;
    
    // Base opacity: reduced to ensure pieces are visible
    const baseOpacity = 0.15 + (v * 0.25);
    
    if (i >= colors.length - 1) {
      const [r, g, b] = colors[colors.length - 1];
      return `rgba(${r}, ${g}, ${b}, ${baseOpacity})`;
    }
    
    const [r1, g1, b1] = colors[i];
    const [r2, g2, b2] = colors[i + 1];
    
    const r = Math.round(r1 + f * (r2 - r1));
    const g = Math.round(g1 + f * (g2 - g1));
    const b = Math.round(b1 + f * (b2 - b1));
    
    return `rgba(${r}, ${g}, ${b}, ${baseOpacity})`;
  };

  return (
    <div className="absolute inset-0 pointer-events-none grid grid-cols-8 grid-rows-8 z-10 rounded-md overflow-hidden mix-blend-multiply dark:mix-blend-screen">
      {displayRanks.map(rank =>
        displayFiles.map(file => {
          const square = `${file}${rank}`;
          const value = tensionMatrix[square] || 0;
          return (
            <div
              key={square}
              className="w-full h-full border border-black/50 dark:border-white/50 transition-colors duration-500 ease-in-out"
              style={{
                backgroundColor: getHeatmapColor(value),
              }}
            />
          );
        })
      )}
    </div>
  );
});
