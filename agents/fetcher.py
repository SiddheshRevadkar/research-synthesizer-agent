"""
Fetcher Agent: Uses Tavily API to search web.
"""

import os
from utils.state import AgentState
from dotenv import load_dotenv
from tavily import TavilyClient

# Load environment variables
load_dotenv()


def fetcher_node(state: AgentState) -> AgentState:
    print("🔹 Running Fetcher Node...")

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise Exception("❌ Tavily API key not found")

    client = TavilyClient(api_key=api_key)

    results = []

    try:
        for question in state.get("sub_questions", []):

            # ✅ SAFETY: validate question
            if not isinstance(question, str):
                print("⚠️ Skipping non-string question:", question)
                continue

            question = question.strip()

            if not question:
                print("⚠️ Skipping empty question")
                continue

            print(f"🔍 Searching: {question}")

            try:
                response = client.search(query=question)
            except Exception as api_error:
                print(f"⚠️ Tavily error for question '{question}': {api_error}")
                continue

            # ✅ Validate response structure
            if not response or "results" not in response:
                print("⚠️ Invalid response format")
                continue

            for r in response["results"][:3]:
                content = r.get("content", "")
                url = r.get("url", "")

                # ✅ Skip bad results
                if not content or not url:
                    continue

                results.append({
                    "question": question,
                    "content": content,
                    "url": url
                })

        if not results:
            raise Exception("No valid search results found from Tavily")

        state["search_results"] = results

    except Exception as e:
        raise Exception(f"Fetcher Error: {str(e)}")

    return state