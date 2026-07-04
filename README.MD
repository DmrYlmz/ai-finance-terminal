# 📈 AI-Powered Financial Analysis Terminal

An intelligent, multi-agent financial analysis platform built with **LangGraph**, **FastAPI**, and **Streamlit**. This project utilizes a Map-Reduce architecture to perform concurrent technical and fundamental analysis on single assets or entire portfolios.

## 🚀 Features

- **Multi-Agent Architecture:** Leverages LangGraph to orchestrate specialized AI agents (Data Fetcher, Technical Analyst, Sentiment Analyzer, Strategy Orchestrator).
- **Map-Reduce Portfolio Analysis:** Analyzes multiple assets in parallel, dramatically reducing processing time, and synthesizes the data into a cohesive portfolio summary.
- **Advanced Technical Indicators:** Calculates TradingView-standard RMA-based RSI, MACD, SMA-20, and Bollinger Bands using Pandas.
- **Multilingual i18n Support:** Fully internationalized UI and AI outputs. Users can switch dynamically between English (EN), German (DE), and Turkish (TR).
- **Robust Error Handling:** Implements fallback mechanisms for API limits and missing market data.

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.10+
- **AI & Orchestration:** LangGraph, LangChain, Google Gemini (LLM)
- **Frontend:** Streamlit, Plotly (for interactive candlestick charts)
- **Data Processing:** `yfinance`, Pandas, NumPy

## 🧠 System Architecture

The system follows a directed graph workflow where parallel processing is handled via LangGraph nodes:


graph TD;
    A[User Input] --> B(FastAPI Endpoint);
    B --> C{Graph State Initiated};
    C --> D[Data Fetcher Agent];
    D --> E[Technical Analysis Agent];
    D --> F[Sentiment Analysis Agent];
    E --> G[Strategy Orchestrator];
    F --> G;
    G --> H[Final Decision: BUY/SELL/HOLD];
    H --> I[Streamlit Dashboard];
⚙️ Installation & Setup
Prerequisites
Make sure you have Python 3.10+ and Git installed on your system.

1. Clone the repository
Bash
git clone https://github.com/DmrYlmz/ai-finance-terminal.git
cd ai-finance-terminal
2. Install dependencies
Bash
pip install -r requirements.txt
3. Environment Variables
Create a .env file in the root directory and add your API keys:

Kod snippet'i
GOOGLE_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
4. Run the Application
You will need two separate terminal windows to run the backend and frontend simultaneously.

Terminal 1: Run the Backend (FastAPI)

Bash
uvicorn main:app --reload
Terminal 2: Run the Frontend (Streamlit)

Bash
streamlit run dashboard.py
🔮 Future Enhancements
Computer Vision Integration: Analyze chart patterns (Head & Shoulders, Double Bottom) via multimodal LLMs.

Arbitrage Tracking: Adding custom web-scraping agents to track arbitrage opportunities across different regional markets.
