import sys
import os

# Add root to python path to import ai module properly if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.interface import conversational_recommend

def test_rag():
    query = "Recommend dark sci-fi movies"
    
    print(f"\n--- Testing RAG Pipeline ---")
    print(f"User Query: {query}\n")
    
    print("Generating response (this may take a few seconds)...")
    try:
        response = conversational_recommend(query)
        print("\n--- Assistant Response ---")
        print(response)
        print("--------------------------\n")
    except Exception as e:
        print(f"Error during RAG test: {e}")

if __name__ == "__main__":
    test_rag()
