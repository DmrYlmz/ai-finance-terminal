"""
(3B) FUNDAMENTAL ANALYSIS AGENT - rag_agent
The ReAct sub-agent is triggered: The LLM autonomously calls the Tavily Search Tool
to search for recent news regarding the symbol and classifies the overall market
sentiment as POSITIVE / NEGATIVE / NEUTRAL.

Note: create_react_agent is LangGraph's built-in factory for ReAct agents.
"""
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from state import PortfolioState

SYSTEM_PROMPT = (
    "You are a financial news analyst. Use the Tavily search tool to investigate "
    "significant news from the last 7 days for the given symbol. "
    "Based on the news, determine the overall market sentiment. "
    "On the VERY LAST line of your response, write exactly in this format with no additional text:\n"
    "SENTIMENT: POSITIVE\n"
    "(or NEGATIVE or NEUTRAL)"
)

_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        search_tool = TavilySearch(max_results=5)
        _agent = create_react_agent(llm, tools=[search_tool], prompt=SYSTEM_PROMPT)
    return _agent


def _extract_sentiment(text: str) -> str:
    match = re.search(r"SENTIMENT:\s*(POZİTİF|NEGATİF|NÖTR)", text.upper())
    return match.group(1) if match else "NÖTR"


def rag_agent(state: PortfolioState) -> PortfolioState:
    if state.get("error"):
        return {}

    symbol = state["symbol"]
    agent = _get_agent()

    result = agent.invoke({
        "messages": [(
            "user",
            f"{symbol} hakkında son haberleri araştır ve piyasa duyarlılığını belirle."
        )]
    })

    raw_content = result["messages"][-1].content
    
    if isinstance(raw_content, list):
        text_content = " ".join(
            block.get("text", "") for block in raw_content if isinstance(block, dict)
        )
    else:
        text_content = str(raw_content)

    sentiment = _extract_sentiment(text_content)

    return {
        "sentiment": sentiment,
        "sentiment_summary": text_content,
    }