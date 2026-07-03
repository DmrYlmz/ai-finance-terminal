from langchain_google_genai import ChatGoogleGenerativeAI
from state import PortfolioMapState

PROMPT_TEMPLATE = """Below are the individual analysis results for the assets in the user's portfolio:

{asset_reports}

Objective:
1. Evaluate the overall status and performance of these assets from the perspective of a "Portfolio Manager".
2. Assess the risk distribution within the portfolio (e.g., is it heavily concentrated in crypto, or well-balanced with traditional equities?).
3. Propose a comprehensive action plan (e.g., realize profits on outperforming assets, accumulate on dips).

Write a 3-4 sentence summary in English using a highly professional and financial tone.
"""

def portfolio_manager(state: PortfolioMapState) -> PortfolioMapState:
    if not state.get("results"):
        return {"portfolio_summary": "Analiz edilecek varlık bulunamadı."}
    reports_text = ""
    for res in state["results"]:
        reports_text += f"\n--- {res.get('symbol')} ---\n"
        reports_text += f"Anlık Fiyat: {res.get('current_price')}\n"
        reports_text += f"Strateji: {res.get('strategy')}\n"

    llm = ChatGoogleGenerativeAI(model="gemini-3.1-pro-preview", temperature=0)
    prompt = PROMPT_TEMPLATE.format(asset_reports=reports_text)
    
    response = llm.invoke(prompt)
    return {"portfolio_summary": response.content}