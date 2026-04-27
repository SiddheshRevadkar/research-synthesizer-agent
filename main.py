"""
FastAPI backend for Research Agent.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from graph.pipeline import build_graph
from utils.state import AgentState
import time
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
graph = build_graph()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestBody(BaseModel):
    topic: str


@app.get("/")
def home():
    return {"message": "Research Agent API is running"}


@app.post("/research")
async def research(data: RequestBody):
    start = time.time()

    state: AgentState = {
        "topic": data.topic,
        "sub_questions": [],
        "search_results": [],
        "retrieved_chunks": [],
        "final_report": "",
        "sources": []
    }

    try:
        result = graph.invoke(state)

        return {
            "report": result["final_report"],
            "sources": result["sources"],
            "time_taken": round(time.time() - start, 2)
        }

    except Exception as e:
        return {"error": str(e)}