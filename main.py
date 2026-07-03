"""
FastAPI - The System's API Gateway

POST /analyze {"symbol": "ETH-USD"}
    -> Initializes the PortfolioState, executes the LangGraph workflow,
       and returns only the requested summary data from the finalized state as a JSON response.
"""
from typing import Optional
from multi_graph import compiled_multi_graph
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from graph import compiled_graph  
from multi_graph import compiled_multi_graph


app = FastAPI(
    title="Kripto / Hisse Analiz Ajanı",
    description="LangGraph tabanlı çok-ajanlı teknik + temel analiz servisi",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    symbol: str
    entry_price: Optional[float] = None       
    investment_horizon: Optional[str] = "ORTA"
    language: Optional[str] = "TR"

class AnalyzeResponse(BaseModel):
    symbol: str
    current_price: Optional[float] = None  
    rsi: Optional[float] = None
    sentiment: Optional[str] = None
    strategy: Optional[str] = None
    error: Optional[str] = None

class PortfolioRequest(BaseModel):
    assets: list[dict]
    language: Optional[str] = "TR" 

@app.post("/analyze_portfolio")
def analyze_portfolio(request: PortfolioRequest):
    initial_state = {"assets": request.assets}
    
    try:
        result = compiled_multi_graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portföy grafik hatası: {e}")

    
    return {
        "portfolio_summary": result.get("portfolio_summary"),
        "individual_results": result.get("results", [])
    }
    
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    if not request.symbol or not request.symbol.strip():
        raise HTTPException(status_code=400, detail="symbol alanı boş olamaz.")

    initial_state = {
        "symbol": request.symbol.upper().strip(),
        "entry_price": request.entry_price,
        "investment_horizon": request.investment_horizon.upper().strip(),
        "language": request.language,
    }
    
    try:
        result = compiled_graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grafik çalıştırma hatası: {e}")

    return AnalyzeResponse(
        symbol=result.get("symbol", request.symbol),
        current_price=result.get("current_price"),  
        rsi=result.get("rsi"),
        sentiment=result.get("sentiment"),
        strategy=result.get("strategy"),
        error=result.get("error"),
    )


@app.get("/health")
def health():
    return {"status": "ok"}
