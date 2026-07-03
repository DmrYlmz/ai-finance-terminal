"""
(3A) TECHNICAL AGENT - tech_agent
Reads the price data from the state, calculates the RSI (Relative Strength Index),
and appends the result to the state. No LLM call -> fast, deterministic, cost-free.
"""
import pandas as pd
import numpy as np
from state import PortfolioState

def calculate_indicators(closes: list[float]):
    series = pd.Series(closes)
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, min_periods=14, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi = np.where(avg_loss == 0, 100.0, rsi)
    rsi = pd.Series(rsi, index=series.index) 
    sma_20 = series.rolling(window=20).mean()
    std_20 = series.rolling(window=20).std()
    bollinger_upper = sma_20 + (std_20 * 2)
    bollinger_lower = sma_20 - (std_20 * 2)
    ema_12 = series.ewm(span=12, adjust=False).mean()
    ema_26 = series.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26

    return {
        "rsi": float(rsi.dropna().iloc[-1]) if not rsi.dropna().empty else 50.0,
        "sma_20": float(sma_20.dropna().iloc[-1]) if not sma_20.dropna().empty else 0.0,
        "bollinger_upper": float(bollinger_upper.dropna().iloc[-1]) if not bollinger_upper.dropna().empty else 0.0,
        "bollinger_lower": float(bollinger_lower.dropna().iloc[-1]) if not bollinger_lower.dropna().empty else 0.0,
        "macd": float(macd_line.dropna().iloc[-1]) if not macd_line.dropna().empty else 0.0,
    }

def tech_agent(state: PortfolioState) -> PortfolioState:
    if state.get("error") or not state.get("price_data"):
        return {}

    closes = state["price_data"]["close"]
    
    
    if len(closes) < 2:
        return {"rsi": 50.0}

    indicators = calculate_indicators(closes)
    
    
    result = {}
    if indicators["rsi"] != 50.0 or len(closes) >= 15:
        result["rsi"] = round(indicators["rsi"], 2)
    if indicators["sma_20"] != 0.0:
        result["sma_20"] = round(indicators["sma_20"], 2)
    if indicators["bollinger_upper"] != 0.0:
        result["bollinger_upper"] = round(indicators["bollinger_upper"], 2)
        result["bollinger_lower"] = round(indicators["bollinger_lower"], 2)
    if indicators["macd"] != 0.0:
        result["macd"] = round(indicators["macd"], 2)

    if not result:
        return {"rsi": 50.0}
        
    return result