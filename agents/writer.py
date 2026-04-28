"""
Writer Agent: Generates final research report.
"""

from langchain_groq import ChatGroq
from utils.state import AgentState
from dotenv import load_dotenv
import os

load_dotenv()

def writer_node(state: AgentState) -> AgentState:
    print("🔹 Running Writer Node...")

    
    llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)

    context = "\n\n".join(state["retrieved_chunks"])

    prompt = f"""
    Write a structured research report.

    Topic: {state['topic']}

    Use this context:
    {context}

    Requirements:
    - Title
    - Executive Summary (2 sentences)
    - Separate sections for each sub-question
    - Use inline citations like [1], [2]
    - Add Key Takeaways (bullet points)
    - Add References with URLs

    Make it professional and concise.
    """

    try:
        response = llm.invoke(prompt)
        state["final_report"] = response.content

    except Exception as e:
        raise Exception(f"Writer Error: {str(e)}")

    return state