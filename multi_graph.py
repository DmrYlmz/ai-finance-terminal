from langgraph.graph import StateGraph, END
from langgraph.constants import Send
from state import PortfolioMapState, PortfolioState
from graph import compiled_graph as single_asset_graph 
from agents.portfolio_agent import portfolio_manager

def map_assets(state: PortfolioMapState):
    sends = []
    for asset in state["assets"]:
        initial_asset_state = {
            "symbol": asset["symbol"],
            "entry_price": asset.get("entry_price"),
            "investment_horizon": asset.get("investment_horizon", "ORTA")
        }
        sends.append(Send("process_single_asset", initial_asset_state))
    return sends

def process_single_asset_wrapper(state: PortfolioState):
    result = single_asset_graph.invoke(state)
    return {"results": [result]}


def build_multi_graph():
    builder = StateGraph(PortfolioMapState)
    builder.add_node("process_single_asset", process_single_asset_wrapper)
    builder.add_node("portfolio_manager", portfolio_manager)
    builder.add_conditional_edges("__start__", map_assets, ["process_single_asset"])
    builder.add_edge("process_single_asset", "portfolio_manager")
    builder.add_edge("portfolio_manager", END)
    return builder.compile()

compiled_multi_graph = build_multi_graph()