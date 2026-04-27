"""
Defines the shared AgentState used across all nodes.
"""

from typing import TypedDict, List, Dict


class AgentState(TypedDict):
    topic: str
    sub_questions: List[str]
    search_results: List[Dict]
    retrieved_chunks: List[str]
    final_report: str
    sources: List[str]