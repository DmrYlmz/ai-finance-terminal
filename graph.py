from langgraph.graph import StateGraph, END
from state import PortfolioState
from agents.market_data import fetch_market_data
from agents.tech_agent import tech_agent
from agents.rag_agent import rag_agent
from agents.predictive_agent import predictive_agent 
from agents.strategy_agent import strategy_orchestrator

def build_graph():
    graph = StateGraph(PortfolioState)

    graph.add_node("fetch_market_data", fetch_market_data)
    graph.add_node("tech_agent", tech_agent)
    graph.add_node("rag_agent", rag_agent)
    graph.add_node("predictive_agent", predictive_agent) 
    graph.add_node("strategy_orchestrator", strategy_orchestrator)

    graph.set_entry_point("fetch_market_data")

    
    graph.add_edge("fetch_market_data", "tech_agent")
    graph.add_edge("fetch_market_data", "rag_agent")
    graph.add_edge("fetch_market_data", "predictive_agent") 

    
    graph.add_edge("tech_agent", "strategy_orchestrator")
    graph.add_edge("rag_agent", "strategy_orchestrator")
    graph.add_edge("predictive_agent", "strategy_orchestrator") 

    graph.add_edge("strategy_orchestrator", END)

    return graph.compile()

compiled_graph = build_graph()