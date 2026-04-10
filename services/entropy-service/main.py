import math
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Entropy Service", description="Calculates Shannon Entropy and Tension Matrix from chess engine lines.")

class EngineLine(BaseModel):
    uci_move: str = Field(..., description="UCI format move, e.g., 'e2e4'")
    cp_score: float = Field(..., description="Centipawn evaluation score")

class HeatmapResponse(BaseModel):
    total_entropy: float
    tension_matrix: Dict[str, float]

def calculate_softmax(scores: List[float], temperature: float = 50.0) -> List[float]:
    if not scores:
        return []
    # Find max for numerical stability
    max_score = max(scores)
    
    # Calculate exponentials
    exps = [math.exp((score - max_score) / temperature) for score in scores]
    
    # Sum of exponentials
    sum_exps = sum(exps)
    
    # Normalize
    if sum_exps == 0:
        return [1.0 / len(scores)] * len(scores)
        
    return [e / sum_exps for e in exps]

def calculate_shannon_entropy(probabilities: List[float]) -> float:
    entropy = 0.0
    for p in probabilities:
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

@app.post("/heatmap", response_model=HeatmapResponse)
async def generate_heatmap(lines: List[EngineLine]):
    if not lines:
        return HeatmapResponse(total_entropy=0.0, tension_matrix={})
        
    # 1. Softmax
    scores = [line.cp_score for line in lines]
    probabilities = calculate_softmax(scores, temperature=50.0)
    
    # 2. Total Shannon Entropy
    total_entropy = calculate_shannon_entropy(probabilities)
    
    # 3. Create empty dict and populate
    tension_matrix = {}
    for line, prob in zip(lines, probabilities):
        move = line.uci_move
        if len(move) >= 4:
            origin = move[:2]
            target = move[2:4]
            tension_matrix[origin] = tension_matrix.get(origin, 0.0) + prob
            tension_matrix[target] = tension_matrix.get(target, 0.0) + prob
            
    # 4. Normalize tension matrix
    if tension_matrix:
        max_tension = max(tension_matrix.values())
        if max_tension > 0:
            for square in tension_matrix:
                tension_matrix[square] = float(tension_matrix[square] / max_tension)
                
    return HeatmapResponse(
        total_entropy=total_entropy,
        tension_matrix=tension_matrix
    )
