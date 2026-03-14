from fastapi import FastAPI
from schema import QueryRequest , QueryResponse , AgentState
from agentic_rag import ask_question


app = FastAPI(
    title="CampusAI API",
    version="1.0.0"
)

@app.get("/home")
def home_function():
    return {"Response" :"API is running live."}

@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    state = AgentState(question=request.question)
    result = ask_question(state)
    return QueryResponse(answer=result["ans"])
