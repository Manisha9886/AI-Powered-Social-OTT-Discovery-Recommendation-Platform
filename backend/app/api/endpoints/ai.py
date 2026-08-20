import os
import json
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

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'processed')
LOOKUP_PATH = os.path.join(PROCESSED_DIR, 'movie_lookup.json')
movies_lookup: Dict[str, Any] = {}
try:
    with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
        movies_lookup = json.load(f)
except Exception:
    pass

def generate_dynamic_fallback(query: str) -> str:
    query_words = [w.lower().strip() for w in query.split() if len(w.strip()) > 2]
    matched = []
    
    for m_id, m_data in movies_lookup.items():
        title = str(m_data.get("title", "")).lower()
        genres = " ".join(m_data.get("genres", [])).lower() if isinstance(m_data.get("genres"), list) else str(m_data.get("genres", "")).lower()
        keywords = " ".join(m_data.get("keywords", [])).lower() if isinstance(m_data.get("keywords"), list) else str(m_data.get("keywords", "")).lower()
        rating = float(m_data.get("vote_average", 0) or 0)
        
        matches = sum(1 for w in query_words if w in genres or w in keywords or w in title)
        if matches > 0:
            matched.append((matches, rating, m_data))
            
    matched.sort(key=lambda x: (x[0], x[1]), reverse=True)
    top_candidates = [m for sc, r, m in matched[:5]]
    
    if not top_candidates:
        top_candidates = list(movies_lookup.values())[:5]
        
    lines = [f"Based on your query '{query}', here are top recommendations:\n"]
    for idx, m in enumerate(top_candidates, start=1):
        t_str = m.get("title", "Movie")
        year = m.get("release_year", "")
        genres = ", ".join(m.get("genres", [])) if isinstance(m.get("genres"), list) else str(m.get("genres", ""))
        rating = m.get("vote_average", "7.0")
        lines.append(f"{idx}. {t_str} ({year})")
        lines.append(f"   Genre: {genres}")
        lines.append(f"   Rating: {rating}/10\n")
        
    return "\n".join(lines).strip()

@router.post("/recommend")
def ai_recommend(request: QueryRequest):
    """
    End-to-end RAG conversational recommendation.
    """
    try:
        res = conversational_recommend(request.query)
        if not res or not isinstance(res, str) or not res.strip():
            res = generate_dynamic_fallback(request.query)
        return {"response": res}
    except Exception as e:
        print(f"ai_recommend endpoint exception: {e}")
        return {"response": generate_dynamic_fallback(request.query)}
