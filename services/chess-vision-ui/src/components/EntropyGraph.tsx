import React from 'react';
import {
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

export interface EntropyDataPoint {
  ply: number;
  entropy: number;
}

interface EntropyGraphProps {
  data: EntropyDataPoint[];
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const moveNumber = Math.ceil(data.ply / 2);
    const color = data.ply % 2 === 1 ? 'White' : 'Black';
    return (
      <div className="bg-slate-900 border border-slate-700 text-slate-100 p-3 rounded-lg shadow-xl shadow-black/50 text-sm">
        <p className="font-semibold mb-1 text-cyan-400">Move {moveNumber} {color}</p>
        <p className="text-slate-300">Entropy: <span className="font-mono text-white">{data.entropy.toFixed(3)}</span></p>
      </div>
    );
  }
  return null;
};

export const EntropyGraph: React.FC<EntropyGraphProps> = ({ data }) => {
  if (!data || data.length === 0) return null;

  return (
    <div className="w-full h-40 mt-4 bg-card/40 border border-border/50 rounded-xl overflow-hidden shadow-inner p-2.5">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 2 }} />
          <Line
            type="monotone"
            dataKey="entropy"
            stroke="#06b6d4" // tailwind cyan-500
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, fill: '#22d3ee', stroke: '#083344', strokeWidth: 2 }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
