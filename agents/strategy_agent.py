"""
(4) DECISION AGENT - strategy_orchestrator
Executes after the parallel branches converge (fan-in).
Retrieves the RSI and Sentiment data from the state, interprets them using the LLM (GPT-4o),
and appends the final "BUY" / "SELL" / "HOLD" decision to the state.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from state import PortfolioState

PROMPT_TEMPLATE = """Propose a CUSTOMIZED investment strategy for {symbol} based on the comprehensive data below.

--- USER PORTFOLIO INFORMATION ---
Investment Horizon: {investment_horizon} TERM (For short-term, RSI/News are crucial; for medium/long-term, macro outlook/AI prediction take precedence)
User's Entry Price (Cost Basis): {entry_price}
Current Live Price: {current_price}
Current Profit/Loss Status: {profit_loss_status}

--- TECHNICAL INDICATORS ---
RSI (14): {rsi} | MACD: {macd} | SMA (20-Day): {sma_20}
Bollinger Bands: Upper={bollinger_upper}, Lower={bollinger_lower}

--- AI PREDICTION (LSTM) ---
Short-Term Directional Expectation: {dl_prediction}

--- FUNDAMENTAL ANALYSIS ---
News Sentiment: {sentiment}
Sentiment Rationale: {sentiment_summary}

Objective:
1. Strictly adhere to the selected investment horizon ({investment_horizon}).
2. If the user's entry price ({entry_price}) is provided, compare it with the current price to formulate a take-profit or stop-loss strategy. If no cost basis is provided, interpret it as a general market entry opportunity.
3. Clearly state your final decision as "BUY", "SELL", or "WAIT" (or "HOLD" if already in the portfolio). Include a 2-3 sentence financial rationale.
CRITICAL RULE: You MUST write your response EXACTLY in {target_language}. Use financial terminology appropriately aligned with the selected language.
"""
def strategy_orchestrator(state: PortfolioState) -> PortfolioState:
    if state.get("error"):
        return {"strategy": f"Hata nedeniyle analiz tamamlanamadı: {state['error']}"}

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    entry = state.get("entry_price")
    current = state.get("current_price")
    pl_text = "Bilinmiyor (Portföyde değil, yeni alım için bakılıyor)"
    if entry and current:
        perf = ((current - entry) / entry) * 100
        pl_text = f"%{perf:.2f} " + ("KÂRDA" if perf >= 0 else "ZARARDA")

    lang_code = state.get("language", "TR") 
    lang_map = {"TR": "Turkish", "EN": "English", "DE": "German"}
    target_lang = lang_map.get(lang_code, "Turkish")

    prompt = PROMPT_TEMPLATE.format(
        symbol=state.get("symbol"),
        investment_horizon=state.get("investment_horizon", "ORTA"),
        entry_price=entry if entry else "Belirtilmedi",
        current_price=current if current else "Belirtilmedi",
        profit_loss_status=pl_text,
        rsi=state.get("rsi", "bilinmiyor"),
        macd=state.get("macd", "bilinmiyor"),
        sma_20=state.get("sma_20", "bilinmiyor"),
        bollinger_upper=state.get("bollinger_upper", "bilinmiyor"),
        bollinger_lower=state.get("bollinger_lower", "bilinmiyor"),
        dl_prediction=state.get("dl_prediction", "bilinmiyor"),
        sentiment=state.get("sentiment", "bilinmiyor"),
        sentiment_summary=(state.get("sentiment_summary") or "")[:600],
        target_language=target_lang 
    )

    response = llm.invoke(prompt)
    return {"strategy": response.content}