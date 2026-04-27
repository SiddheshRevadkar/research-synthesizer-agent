"""
Planner Agent: Generates sub-questions from topic.
"""

import json
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from utils.state import AgentState

load_dotenv()


def planner_node(state: AgentState) -> AgentState:
    print("🔹 Running Planner Node...")

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )

    prompt = f"""
    Generate exactly 3 to 5 clear, concise research questions.

    Rules:
    - Each must be a proper question
    - No empty strings
    - No numbering
    - No explanations
    - Return ONLY JSON array

    Topic: {state['topic']}
    """

    try:
        response = llm.invoke(prompt)

        raw_output = response.content.strip()
        print("Planner raw output:", raw_output)

        sub_questions = json.loads(raw_output)

        # ✅ CLEAN + VALIDATE
        clean_questions = []

        for q in sub_questions:
            if isinstance(q, str):
                q = q.strip()
                if len(q) > 5:  # avoid junk
                    clean_questions.append(q)

        if not clean_questions:
            raise Exception("Planner returned no valid questions")

        state["sub_questions"] = clean_questions[:5]

        print("Final sub-questions:", state["sub_questions"])

    except Exception as e:
        raise Exception(f"Planner Error: {str(e)}")

    return state