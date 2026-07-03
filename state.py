"""
PortfolioState: The shared state carried across nodes throughout the LangGraph graph
(referred to as the 'basket' / conveyor belt in your diagram).

total=False -> all fields are optional; nodes update the state by only 
appending the specific fields they generate (partial update).
"""
from typing import TypedDict, Optional, List, Annotated
import operator

class AssetInput(TypedDict):
    symbol: str
    entry_price: Optional[float]
    investment_horizon: str

class PriceData(TypedDict, total=False):
    dates: List[str]
    close: List[float]
    high: List[float]
    low: List[float]
    volume: List[float]

class PortfolioMapState(TypedDict):
    assets: List[AssetInput]
    results: Annotated[List[dict], operator.add]
    portfolio_summary: Optional[str] 


class PortfolioState(TypedDict, total=False):
    symbol: str
    current_price: Optional[float]
    entry_price: Optional[float]
    investment_horizon: Optional[str]
    language: str
    price_data: Optional[PriceData]
    rsi: Optional[float]
    macd: Optional[float]              
    sma_20: Optional[float]            
    bollinger_upper: Optional[float]   
    bollinger_lower: Optional[float]   
    dl_prediction: Optional[str]       
    sentiment: Optional[str]
    sentiment_summary: Optional[str]
    strategy: Optional[str]
    error: Optional[str]