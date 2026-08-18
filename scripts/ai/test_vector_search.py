import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.vector_store import MovieVectorStore

def test_vector_search():
    print("Testing Vector Store initialization...")
    try:
        vs = MovieVectorStore()
        print("Pinecone connection successful and index accessible.")
    except Exception as e:
        print(f"Error initializing Vector Store: {e}")
        return

    queries = [
        "dark sci-fi movies",
        "psychological thriller",
        "funny family movie",
        "action movies",
        "romantic movies"
    ]

    print("\nTesting Semantic Retrieval...")
    for query in queries:
        print(f"\n--- Query: '{query}' ---")
        try:
            results = vs.search_movies(query, top_k=3)
            for cand in results:
                print(f"[{cand['score']:.4f}] ID: {cand['movie_id']} | Title: {cand['title']}")
        except Exception as e:
            print(f"Error during search: {e}")

if __name__ == "__main__":
    test_vector_search()
