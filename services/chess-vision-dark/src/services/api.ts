const ENTROPY_SERVICE_URL = 'http://localhost:8001';

export interface EngineLine {
  cp_score: number | null;
  mate_score: number | null;
  pv: string;
  centipawn?: number;
  cp?: number;
  mate?: number | null;
}

export interface AnalysisResponse {
  total_entropy: number;
  tension_matrix: Record<string, number>;
  engine_lines: EngineLine[];
}

export async function analyzePosition(fen: string): Promise<AnalysisResponse> {
  const response = await fetch(`${ENTROPY_SERVICE_URL}/analyze_and_map`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ fen }),
  });

  if (!response.ok) {
    throw new Error('Failed to analyze position');
  }

  return response.json();
}
