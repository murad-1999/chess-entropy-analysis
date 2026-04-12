import math
import os
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

app = FastAPI(title="Entropy Service", description="Calculates Shannon Entropy and Tension Matrix from chess engine lines.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EngineLine(BaseModel):
    uci_move: Optional[str] = Field(None, description="UCI format move, e.g., 'e2e4'")
    pv: Optional[str] = Field(None, description="Principal Variation from engine")
    centipawn: Optional[float] = Field(None, description="Centipawn evaluation score")
    cp: Optional[float] = Field(None, description="Raw CP from engine")
    mate: Optional[int] = Field(None, description="Mate in X moves")

class HeatmapResponse(BaseModel):
    total_entropy: float
    tension_matrix: Dict[str, float]

class AnalyzeRequest(BaseModel):
    fen: str

class AnalyzeAndMapResponse(BaseModel):
    engine_lines: List[Dict[str, Any]]
    total_entropy: float
    tension_matrix: Dict[str, float]

def calculate_softmax(scores: List[float], temperature: float = 1.0) -> List[float]:
    if not scores:
        return []
    max_score = max(scores)
    exps = [math.exp((score - max_score) / temperature) for score in scores]
    sum_exps = sum(exps)
    if sum_exps == 0:
        return [1.0 / len(scores)] * len(scores)
    return [e / sum_exps for e in exps]

def calculate_shannon_entropy(probabilities: List[float]) -> float:
    entropy = 0.0
    for p in probabilities:
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def get_effective_score(mate: Optional[int], cp: Optional[float], centipawn: Optional[float], cp_score: Optional[float] = None) -> float:
    if mate is not None:
        return 10000.0 if mate > 0 else -10000.0
    if centipawn is not None:
        return float(centipawn)
    if cp is not None:
        return float(cp)
    if cp_score is not None:
        return float(cp_score)
    return 0.0

def get_move_from_line(line: EngineLine) -> str:
    if line.uci_move:
        return line.uci_move
    if line.pv:
        return line.pv.split()[0]
    return ""

def process_lines(lines: List[EngineLine]) -> tuple[float, Dict[str, float]]:
    if not lines:
        return 0.0, {}
        
    scores = [get_effective_score(line.mate, line.cp, line.centipawn) for line in lines]
    probabilities = calculate_softmax(scores, temperature=1.0)
    total_entropy = calculate_shannon_entropy(probabilities)
    
    tension_matrix = {}
    for line, prob in zip(lines, probabilities):
        move = get_move_from_line(line)
        if len(move) >= 4:
            origin = move[:2]
            target = move[2:4]
            tension_matrix[origin] = tension_matrix.get(origin, 0.0) + prob
            tension_matrix[target] = tension_matrix.get(target, 0.0) + prob
            
    if tension_matrix:
        max_tension = max(tension_matrix.values())
        if max_tension > 0:
            for square in tension_matrix:
                tension_matrix[square] = float(tension_matrix[square] / max_tension)
                
    return total_entropy, tension_matrix

@app.post("/heatmap", response_model=HeatmapResponse)
async def generate_heatmap(lines: List[EngineLine]):
    total_entropy, tension_matrix = process_lines(lines)
    return HeatmapResponse(total_entropy=total_entropy, tension_matrix=tension_matrix)

@app.post("/analyze_and_map", response_model=AnalyzeAndMapResponse)
async def analyze_and_map(request: AnalyzeRequest):
    engine_url = os.environ.get("ENGINE_API_URL", "http://engine-service:8000/analyze")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(engine_url, json={"fen": request.fen}, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"Engine service error: {str(e)}")
            return AnalyzeAndMapResponse(
                engine_lines=[],
                total_entropy=0.0,
                tension_matrix={}
            )
            
    raw_lines = data if isinstance(data, list) else data.get("analysis", data.get("lines", []))
    if not isinstance(raw_lines, list):
        raw_lines = []
        
    engine_lines = [EngineLine(**line) for line in raw_lines]
    total_entropy, tension_matrix = process_lines(engine_lines)
    
    return AnalyzeAndMapResponse(
        engine_lines=raw_lines,
        total_entropy=total_entropy,
        tension_matrix=tension_matrix
    )
