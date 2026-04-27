"""
Defines LangGraph pipeline.
"""

from langgraph.graph import StateGraph
from utils.state import AgentState
from agents.planner import planner_node
from agents.fetcher import fetcher_node
from agents.rag import rag_node
from agents.writer import writer_node


def build_graph():
    print("🔹 Building LangGraph pipeline...")

    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("fetcher", fetcher_node)
    graph.add_node("rag", rag_node)
    graph.add_node("writer", writer_node)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "fetcher")
    graph.add_edge("fetcher", "rag")
    graph.add_edge("rag", "writer")

    return graph.compile()