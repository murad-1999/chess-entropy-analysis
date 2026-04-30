import math
import os
from typing import List, Dict, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

app = FastAPI(title="Analysis Service", description="Calculates standard chess blunders from engine lines.")

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

class AnalyzeRequest(BaseModel):
    fen: str
    prev_fen: Optional[str] = None

class AnalyzeResponse(BaseModel):
    engine_lines: List[Dict[str, Any]]
    eval_cp: float
    mate: Optional[int]
    classification: str

def get_effective_score(mate: Optional[int], cp: Optional[float], centipawn: Optional[float]) -> float:
    if mate is not None:
        return 10000.0 if mate > 0 else -10000.0
    if centipawn is not None:
        return float(centipawn)
    if cp is not None:
        return float(cp)
    return 0.0

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_position(request: AnalyzeRequest):
    engine_url = os.environ.get("ENGINE_API_URL", "http://engine-service:8000/analyze")
    
    async def fetch_eval(fen: str):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(engine_url, json={"fen": fen}, timeout=10.0)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                print(f"Engine service error: {str(e)}")
                return []

    data = await fetch_eval(request.fen)
    raw_lines = data if isinstance(data, list) else data.get("analysis", data.get("lines", []))
    if not isinstance(raw_lines, list):
        raw_lines = []
        
    engine_lines = [EngineLine(**line) for line in raw_lines]
    eval_cp = 0.0
    mate = None
    if engine_lines:
        eval_cp = get_effective_score(engine_lines[0].mate, engine_lines[0].cp, engine_lines[0].centipawn)
        mate = engine_lines[0].mate

    classification = "Book"
    
    if request.prev_fen:
        prev_data = await fetch_eval(request.prev_fen)
        prev_lines = prev_data if isinstance(prev_data, list) else prev_data.get("analysis", prev_data.get("lines", []))
        if isinstance(prev_lines, list) and prev_lines:
            prev_line = EngineLine(**prev_lines[0])
            prev_eval = get_effective_score(prev_line.mate, prev_line.cp, prev_line.centipawn)
            
            is_white_turn = " w " in request.prev_fen
            diff = eval_cp - prev_eval if is_white_turn else prev_eval - eval_cp
            
            if diff <= -300:
                classification = "Blunder"
            elif diff <= -100:
                classification = "Mistake"
            elif diff <= -50:
                classification = "Inaccuracy"
            elif diff >= 0:
                classification = "Best Move"
            else:
                classification = "Good"
    
    return AnalyzeResponse(
        engine_lines=raw_lines,
        eval_cp=eval_cp,
        mate=mate,
        classification=classification
    )

