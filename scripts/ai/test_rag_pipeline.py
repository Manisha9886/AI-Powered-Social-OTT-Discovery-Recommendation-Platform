import os
import sys
from dotenv import load_dotenv

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
load_dotenv()

from ai.rag_pipeline import rag_pipeline_instance
from ai.vector_store import MovieVectorStore

def test_embedding_and_pinecone():
    print("========================================")
    print("TEST 1 & 2: EMBEDDING & PINECONE")
    print("========================================")
    try:
        store = MovieVectorStore()
        query = "Recommend dark sci-fi movies"
        print(f"Query: {query}")
        
        candidates = store.search_movies(query, top_k=3)
        print(f"Pinecone: OK - {len(candidates)} matches")
        for i, c in enumerate(candidates):
            print(f"  Match {i+1}: ID={c.get('movie_id')}, Score={c.get('score'):.4f}")
        return True, candidates
    except Exception as e:
        print(f"FAILED: {e}")
        return False, None

def test_movie_lookup(candidates):
    print("\n========================================")
    print("TEST 3: GROUNDING / MOVIE LOOKUP")
    print("========================================")
    try:
        rag_pipeline_instance.initialize()
        context = rag_pipeline_instance._build_context(candidates)
        print("Grounding: OK - Context Constructed")
        print("Context Snippet:")
        print(context[:500] + "...\n")
        return True, context
    except Exception as e:
        print(f"FAILED: {e}")
        return False, None

def test_llama(context):
    print("\n========================================")
    print("TEST 4: LLAMA GENERATION")
    print("========================================")
    from ai.prompt_templates import rag_prompt
    prompt = rag_prompt.format(user_query="Recommend dark sci-fi movies", context=context)
    try:
        response = rag_pipeline_instance._call_llama(prompt)
        print("LLM: OK - response generated")
        print("Response Snippet:")
        print(response[:200] + "...\n")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

def test_full_rag():
    print("\n========================================")
    print("TEST 5: FULL RAG END-TO-END")
    print("========================================")
    query = "Recommend a psychological thriller"
    try:
        response = rag_pipeline_instance.generate_recommendation(query)
        print("RAG Pipeline: OK")
        print(f"Query: {query}")
        print("Response:")
        print(response)
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

if __name__ == "__main__":
    success, cands = test_embedding_and_pinecone()
    if success and cands:
        success, ctx = test_movie_lookup(cands)
        if success and ctx:
            test_llama(ctx)
    test_full_rag()
