export interface EngineLine {
  cp_score: number | null;
  mate_score: number | null;
  pv: string;
  centipawn?: number;
  cp?: number;
  mate?: number | null;
}

export interface AnalysisResponse {
  engine_lines: EngineLine[];
  eval_cp: number;
  mate: number | null;
  classification: string;
}

export async function analyzePosition(fen: string, prev_fen?: string): Promise<AnalysisResponse> {
  const response = await fetch('/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ fen, prev_fen }),
  });

  if (!response.ok) {
    throw new Error('Failed to analyze position');
  }

  return response.json();
}
