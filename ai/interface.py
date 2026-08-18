from typing import Dict, Any

def understand_query(query: str) -> Dict[str, Any]:
    """
    Extract intent and preferences from a natural language query.
    """
    import json
    import os
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample', 'ai_mock.json')
        with open(data_path, 'r') as f:
            mock_data = json.load(f)
            return mock_data.get("understand_intent_mock", {})
    except Exception:
        return {"intent": "unknown"}

def explain_recommendation(movie_id: int, evidence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a natural language explanation for why a movie was recommended.
    """
    import json
    import os
    try:
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample', 'ai_mock.json')
        with open(data_path, 'r') as f:
            mock_data = json.load(f)
            return mock_data.get("explanation_mock", {})
    except Exception:
        return {"explanation": "Recommended based on your preferences."}
