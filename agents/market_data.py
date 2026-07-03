"""
(2) DATA AGENT - fetch_market_data
Connects to the YFinance API and appends the historical price data of the last 365 days to the state.
This node serves as the sole 'entry point' in the graph;
from here, the workflow diverges into parallel branches for the tech_agent and rag_agent.
"""
import yfinance as yf
import datetime
from state import PortfolioState

def fetch_market_data(state: PortfolioState) -> PortfolioState:
    symbol = state["symbol"]
    try:
        ticker = yf.Ticker(symbol)
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=365) 
        hist = ticker.history(period="1y") 
        
        if hist.empty:
            return {"error": f"'{symbol}' için fiyat verisi bulunamadı."}
        current_price = ticker.info.get("currentPrice") or ticker.info.get("regularMarketPrice")
        
        if current_price is None:
            current_price = float(hist["Close"].iloc[-1])

        current_price = round(current_price, 2)

        price_data = {
            "dates": [d.strftime("%Y-%m-%d") for d in hist.index],
            "close": hist["Close"].tolist(),
            "high": hist["High"].tolist(),
            "low": hist["Low"].tolist(),
            "volume": hist["Volume"].tolist(),
        }
        
        return {
            "price_data": price_data, 
            "current_price": current_price
        } 

    except Exception as e:
        return {"error": f"Veri çekme hatası: {e}"}