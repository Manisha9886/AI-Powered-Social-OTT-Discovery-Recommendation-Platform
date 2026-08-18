import sys
import os

# Add root to python path to import ai module properly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.interface import conversational_recommend

def chat_loop():
    print("==================================================")
    print("🎬 Welcome to the AI Movie Recommender Chatbot 🎬")
    print("==================================================")
    print("(Type 'quit' or 'exit' to stop)\n")
    
    while True:
        try:
            user_input = input("You: ")
            
            if user_input.lower().strip() in ['quit', 'exit']:
                print("\nGoodbye! Have a great movie night! 🍿")
                break
                
            if not user_input.strip():
                continue
                
            print("\n🤖 AI is thinking... (Searching 4,803 movies and generating response)")
            
            response = conversational_recommend(user_input)
            
            print("\n🤖 Assistant:")
            print(response)
            print("-" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye! Have a great movie night! 🍿")
            break
        except Exception as e:
            print(f"\nOops, an error occurred: {e}")

if __name__ == "__main__":
    chat_loop()
