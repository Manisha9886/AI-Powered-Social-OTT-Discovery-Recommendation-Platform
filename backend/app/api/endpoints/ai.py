from fastapi import APIRouter
from ai.interface import understand_query, explain_recommendation, conversational_recommend
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/understand")
def ai_understand(request: QueryRequest):
    """
    Extract intent from query.
    """
    return understand_query(request.query)

class ExplainRequest(BaseModel):
    movie_id: int
    evidence: Dict[str, Any]
    user_query: str = ""

@router.post("/explain")
def ai_explain(request: ExplainRequest):
    """
    Explain a recommendation using Grounded LLM Explainability.
    """
    return explain_recommendation(request.movie_id, request.evidence, request.user_query)

@router.post("/recommend")
def ai_recommend(request: QueryRequest):
    """
    End-to-end RAG conversational recommendation.
    """
    return {"response": conversational_recommend(request.query)}
