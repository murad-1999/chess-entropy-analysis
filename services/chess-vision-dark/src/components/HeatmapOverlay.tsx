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
    
    // We want the heatmap highlight to look like a solid color overlay
    // The user attached a soft, pastel pinkish-red. We will use a gradient
    // from a soft transparent color to that solid pastel red.
    const colors = [
      [82, 171, 230],  // Light Blue
      [242, 203, 94],  // Soft Yellow
      [237, 145, 104], // Soft Orange
      [226, 149, 155], // Pastel Red (from attached image)
    ];
    
    const index = v * (colors.length - 1);
    const i = Math.floor(index);
    const f = index - i;
    
    // Base opacity: use a higher opacity so the color is consistent on light/dark squares
    const baseOpacity = v === 0 ? 0 : 0.4 + (v * 0.5);
    
    if (v === 0) return 'transparent';
    
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
    <div className="absolute inset-0 pointer-events-none grid grid-cols-8 grid-rows-8 z-10 rounded-md overflow-hidden">
      {displayRanks.map(rank =>
        displayFiles.map(file => {
          const square = `${file}${rank}`;
          const value = tensionMatrix[square] || 0;
          return (
            <div
              key={square}
              className="w-full h-full transition-colors duration-500 ease-in-out"
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
